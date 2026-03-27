"""
Dagster observability callbacks for run/op lifecycle integration.

Provides hooks and event handlers that bridge Dagster execution events
to MLFlow, OpenTelemetry, and Prometheus for unified observability.
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


# ---------------------------------------------------------------------------
# Prometheus-style metrics (in-process counters / histograms)
# ---------------------------------------------------------------------------

class DagsterMetrics:
    """
    In-process metrics collector for Dagster runs and ops.

    Maintains counters, histograms, and gauges that can be scraped
    by the ``/api/v1/dagster/metrics`` endpoint in Prometheus format.
    """

    def __init__(self):
        self.runs_total: Dict[str, int] = defaultdict(int)  # {status: count}
        self.asset_materializations_total: Dict[str, int] = defaultdict(int)
        self.run_durations: List[float] = []
        self.op_durations: Dict[str, List[float]] = defaultdict(list)
        self.active_runs: int = 0
        self.queued_runs: int = 0

    def record_run(self, status: str, duration_seconds: float) -> None:
        """Record a completed run."""
        self.runs_total[status] += 1
        self.run_durations.append(duration_seconds)

    def record_op(self, op_name: str, duration_seconds: float) -> None:
        """Record a completed op."""
        self.op_durations[op_name].append(duration_seconds)

    def record_materialization(self, asset_key: str) -> None:
        """Record an asset materialization."""
        self.asset_materializations_total[asset_key] += 1

    def increment_active(self) -> None:
        self.active_runs += 1

    def decrement_active(self) -> None:
        self.active_runs = max(0, self.active_runs - 1)

    def to_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines: List[str] = []

        # Run counters
        lines.append("# HELP dagster_runs_total Total number of Dagster runs by status")
        lines.append("# TYPE dagster_runs_total counter")
        for status, count in self.runs_total.items():
            lines.append(f'dagster_runs_total{{status="{status}"}} {count}')

        # Asset materialization counters
        lines.append(
            "# HELP dagster_asset_materializations_total Total asset materializations"
        )
        lines.append("# TYPE dagster_asset_materializations_total counter")
        for asset, count in self.asset_materializations_total.items():
            lines.append(
                f'dagster_asset_materializations_total{{asset="{asset}"}} {count}'
            )

        # Run duration histogram (simplified - sum and count)
        lines.append("# HELP dagster_run_duration_seconds Run duration in seconds")
        lines.append("# TYPE dagster_run_duration_seconds summary")
        if self.run_durations:
            lines.append(
                f"dagster_run_duration_seconds_sum "
                f"{sum(self.run_durations):.3f}"
            )
            lines.append(
                f"dagster_run_duration_seconds_count {len(self.run_durations)}"
            )

        # Op duration histogram
        lines.append("# HELP dagster_op_duration_seconds Op duration in seconds")
        lines.append("# TYPE dagster_op_duration_seconds summary")
        for op_name, durations in self.op_durations.items():
            if durations:
                lines.append(
                    f'dagster_op_duration_seconds_sum{{op="{op_name}"}} '
                    f"{sum(durations):.3f}"
                )
                lines.append(
                    f'dagster_op_duration_seconds_count{{op="{op_name}"}} '
                    f"{len(durations)}"
                )

        # Gauges
        lines.append("# HELP dagster_active_runs Currently active runs")
        lines.append("# TYPE dagster_active_runs gauge")
        lines.append(f"dagster_active_runs {self.active_runs}")

        lines.append("# HELP dagster_queued_runs Currently queued runs")
        lines.append("# TYPE dagster_queued_runs gauge")
        lines.append(f"dagster_queued_runs {self.queued_runs}")

        return "\n".join(lines) + "\n"


# Global metrics instance
_metrics = DagsterMetrics()


def get_dagster_metrics() -> DagsterMetrics:
    """Get the global Dagster metrics instance."""
    return _metrics


# ---------------------------------------------------------------------------
# Dagster Run Callback
# ---------------------------------------------------------------------------

class DagsterRunCallback:
    """
    Callback handler for Dagster run lifecycle events.

    Integrates with MLFlow, OpenTelemetry, and Prometheus to record
    run-level metrics and traces.

    Example:
        >>> callback = DagsterRunCallback()
        >>> callback.on_run_start(run_id="abc", job_name="etl")
        >>> # ... run executes ...
        >>> callback.on_run_success(run_id="abc", job_name="etl", duration=12.5)
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self._tracker = None
        self._telemetry = None

    @property
    def tracker(self):
        """Lazy-load MLFlow tracker."""
        if self._tracker is None:
            from agentic_assistants.core.mlflow_tracker import MLFlowTracker
            self._tracker = MLFlowTracker(self.config)
        return self._tracker

    @property
    def telemetry(self):
        """Lazy-load telemetry manager."""
        if self._telemetry is None:
            from agentic_assistants.core.telemetry import TelemetryManager
            self._telemetry = TelemetryManager(self.config)
            if self.config.telemetry_enabled:
                self._telemetry.initialize()
        return self._telemetry

    def on_run_start(
        self,
        run_id: str,
        job_name: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Called when a Dagster run starts."""
        _metrics.increment_active()
        logger.info(f"Dagster run started: {job_name} (run_id={run_id})")

        # Start OTEL span
        self.telemetry.span(
            f"dagster.run.{job_name}",
            attributes={
                "dagster.run_id": run_id,
                "dagster.job_name": job_name,
            },
        )

    def on_run_success(
        self,
        run_id: str,
        job_name: str,
        duration_seconds: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Called when a Dagster run succeeds."""
        _metrics.decrement_active()
        _metrics.record_run("success", duration_seconds)

        logger.info(
            f"Dagster run succeeded: {job_name} "
            f"(run_id={run_id}, duration={duration_seconds:.2f}s)"
        )

        # Log to MLFlow
        with self.tracker.start_run(
            run_name=f"dagster-{job_name}-{run_id[:8]}",
            tags={"framework": "dagster", "job_name": job_name, "status": "success"},
        ):
            self.tracker.log_metric("duration_seconds", duration_seconds)
            self.tracker.log_metric("success", 1)
            if metadata:
                self.tracker.log_params(
                    {k: str(v)[:250] for k, v in metadata.items()}
                )

    def on_run_failure(
        self,
        run_id: str,
        job_name: str,
        duration_seconds: float,
        error: Optional[str] = None,
    ) -> None:
        """Called when a Dagster run fails."""
        _metrics.decrement_active()
        _metrics.record_run("failure", duration_seconds)

        logger.error(
            f"Dagster run failed: {job_name} "
            f"(run_id={run_id}, duration={duration_seconds:.2f}s, error={error})"
        )

        with self.tracker.start_run(
            run_name=f"dagster-{job_name}-{run_id[:8]}",
            tags={"framework": "dagster", "job_name": job_name, "status": "failure"},
        ):
            self.tracker.log_metric("duration_seconds", duration_seconds)
            self.tracker.log_metric("success", 0)
            if error:
                self.tracker.set_tag("error", error[:250])


# ---------------------------------------------------------------------------
# Dagster Op Callback
# ---------------------------------------------------------------------------

class DagsterOpCallback:
    """
    Callback handler for Dagster op/step execution events.

    Records per-op metrics and OpenTelemetry spans.
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self._telemetry = None

    @property
    def telemetry(self):
        if self._telemetry is None:
            from agentic_assistants.core.telemetry import TelemetryManager
            self._telemetry = TelemetryManager(self.config)
            if self.config.telemetry_enabled:
                self._telemetry.initialize()
        return self._telemetry

    @contextmanager
    def track_op(
        self,
        op_name: str,
        run_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager that wraps op execution with metrics and tracing.

        Args:
            op_name: Name of the op
            run_id: Parent run ID
            attributes: Additional span attributes

        Yields:
            None
        """
        span_attrs = {"dagster.op_name": op_name}
        if run_id:
            span_attrs["dagster.run_id"] = run_id
        if attributes:
            span_attrs.update(attributes)

        start = time.time()
        try:
            with self.telemetry.span(
                f"dagster.op.{op_name}", attributes=span_attrs
            ):
                yield
        finally:
            duration = time.time() - start
            _metrics.record_op(op_name, duration)

    def on_op_success(self, op_name: str, duration_seconds: float) -> None:
        """Record a successful op execution."""
        _metrics.record_op(op_name, duration_seconds)

    def on_op_failure(
        self, op_name: str, duration_seconds: float, error: Optional[str] = None
    ) -> None:
        """Record a failed op execution."""
        _metrics.record_op(op_name, duration_seconds)
        logger.error(f"Dagster op failed: {op_name} ({error})")

    def on_asset_materialization(self, asset_key: str) -> None:
        """Record an asset materialization event."""
        _metrics.record_materialization(asset_key)
        logger.info(f"Dagster asset materialized: {asset_key}")


# ---------------------------------------------------------------------------
# Dagster hook implementations (if Dagster is available)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# DagsterTelemetry - OpenTelemetry integration following CrewTelemetry pattern
# ---------------------------------------------------------------------------

class DagsterTelemetry:
    """
    OpenTelemetry instrumentation for Dagster jobs, ops, and assets.

    Follows the same pattern as CrewTelemetry, providing context managers
    for tracing job runs, op executions, and asset materializations with
    rich attributes and metrics.
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self.enabled = self.config.telemetry_enabled
        self._telemetry = None
        self._tracer = None
        self._meter = None
        self._job_duration = None
        self._op_duration = None
        self._asset_counter = None
        self._op_counter = None

    @property
    def telemetry(self):
        if self._telemetry is None:
            from agentic_assistants.core.telemetry import TelemetryManager
            self._telemetry = TelemetryManager(self.config)
            if self.enabled:
                self._telemetry.initialize()
        return self._telemetry

    @property
    def tracer(self):
        if self._tracer is None:
            from agentic_assistants.core.telemetry import get_tracer
            self._tracer = get_tracer("agentic-dagster")
        return self._tracer

    @property
    def meter(self):
        if self._meter is None:
            from agentic_assistants.core.telemetry import get_meter
            self._meter = get_meter("agentic-dagster")
        return self._meter

    def _ensure_metrics(self) -> None:
        if self._job_duration is not None:
            return
        try:
            self._job_duration = self.meter.create_histogram(
                "dagster.job.duration",
                description="Dagster job execution duration in seconds",
                unit="s",
            )
            self._op_duration = self.meter.create_histogram(
                "dagster.op.duration",
                description="Dagster op execution duration in seconds",
                unit="s",
            )
            self._asset_counter = self.meter.create_counter(
                "dagster.asset.materializations",
                description="Number of asset materializations",
                unit="1",
            )
            self._op_counter = self.meter.create_counter(
                "dagster.op.executions",
                description="Number of op executions",
                unit="1",
            )
        except Exception as e:
            logger.warning(f"Failed to setup Dagster OTel metrics: {e}")

    @contextmanager
    def trace_job_run(
        self,
        job_name: str,
        run_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Trace a complete Dagster job run.

        Args:
            job_name: Name of the job
            run_id: Dagster run ID
            attributes: Additional span attributes

        Yields:
            Span for the job run
        """
        if not self.enabled:
            yield None
            return

        self._ensure_metrics()
        span_attrs: Dict[str, Any] = {"dagster.job_name": job_name}
        if run_id:
            span_attrs["dagster.run_id"] = run_id
        if attributes:
            span_attrs.update(attributes)

        start = time.time()
        with self.telemetry.span(f"dagster.job.{job_name}", attributes=span_attrs) as span:
            try:
                yield span
                span.set_attribute("dagster.job.success", True)
                _metrics.record_run("success", time.time() - start)
            except Exception as e:
                span.set_attribute("dagster.job.success", False)
                span.set_attribute("dagster.job.error", str(e))
                span.record_exception(e)
                _metrics.record_run("failure", time.time() - start)
                raise
            finally:
                duration = time.time() - start
                span.set_attribute("dagster.job.duration_seconds", duration)
                if self._job_duration:
                    self._job_duration.record(duration, {"dagster.job_name": job_name})

    @contextmanager
    def trace_op_execution(
        self,
        op_name: str,
        run_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Trace a Dagster op execution.

        Args:
            op_name: Name of the op
            run_id: Parent run ID
            attributes: Additional span attributes

        Yields:
            Span for the op execution
        """
        if not self.enabled:
            yield None
            return

        self._ensure_metrics()
        span_attrs: Dict[str, Any] = {"dagster.op_name": op_name}
        if run_id:
            span_attrs["dagster.run_id"] = run_id
        if attributes:
            span_attrs.update(attributes)

        start = time.time()
        with self.telemetry.span(f"dagster.op.{op_name}", attributes=span_attrs) as span:
            try:
                yield span
                span.set_attribute("dagster.op.success", True)
                if self._op_counter:
                    self._op_counter.add(1, {"dagster.op_name": op_name, "success": "true"})
            except Exception as e:
                span.set_attribute("dagster.op.success", False)
                span.set_attribute("dagster.op.error", str(e))
                span.record_exception(e)
                if self._op_counter:
                    self._op_counter.add(1, {"dagster.op_name": op_name, "success": "false"})
                raise
            finally:
                duration = time.time() - start
                span.set_attribute("dagster.op.duration_seconds", duration)
                _metrics.record_op(op_name, duration)
                if self._op_duration:
                    self._op_duration.record(duration, {"dagster.op_name": op_name})

    @contextmanager
    def trace_asset_materialization(
        self,
        asset_key: str,
        group_name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Trace a Dagster asset materialization.

        Args:
            asset_key: Asset key being materialized
            group_name: Asset group name
            attributes: Additional span attributes

        Yields:
            Span for the materialization
        """
        if not self.enabled:
            yield None
            return

        self._ensure_metrics()
        span_attrs: Dict[str, Any] = {"dagster.asset_key": asset_key}
        if group_name:
            span_attrs["dagster.asset_group"] = group_name
        if attributes:
            span_attrs.update(attributes)

        start = time.time()
        with self.telemetry.span(f"dagster.asset.{asset_key}", attributes=span_attrs) as span:
            try:
                yield span
                span.set_attribute("dagster.asset.success", True)
                _metrics.record_materialization(asset_key)
                if self._asset_counter:
                    self._asset_counter.add(1, {"dagster.asset_key": asset_key})
            except Exception as e:
                span.set_attribute("dagster.asset.success", False)
                span.set_attribute("dagster.asset.error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start
                span.set_attribute("dagster.asset.duration_seconds", duration)


_dagster_telemetry: Optional[DagsterTelemetry] = None


def get_dagster_telemetry(config: Optional[AgenticConfig] = None) -> DagsterTelemetry:
    """Get or create the global Dagster telemetry instance."""
    global _dagster_telemetry
    if _dagster_telemetry is None:
        _dagster_telemetry = DagsterTelemetry(config)
    return _dagster_telemetry


# ---------------------------------------------------------------------------
# Dagster hook implementations (if Dagster is available)
# ---------------------------------------------------------------------------

if DAGSTER_AVAILABLE:

    @dg.success_hook
    def otel_success_hook(context: dg.HookContext):
        """Dagster hook that emits OTel spans and Prometheus metrics on op success."""
        op_name = context.op.name
        logger.debug(f"Success hook fired for: {op_name}")
        _metrics.record_op(op_name, 0)

        telemetry = get_dagster_telemetry()
        if telemetry.enabled:
            with telemetry.trace_op_execution(op_name, attributes={"dagster.hook": "success"}):
                pass

    @dg.failure_hook
    def otel_failure_hook(context: dg.HookContext):
        """Dagster hook that emits OTel spans and Prometheus metrics on op failure."""
        op_name = context.op.name
        logger.warning(f"Failure hook fired for: {op_name}")
        _metrics.record_op(op_name, 0)

        telemetry = get_dagster_telemetry()
        if telemetry.enabled:
            with telemetry.trace_op_execution(
                op_name,
                attributes={"dagster.hook": "failure", "dagster.op.success": False},
            ):
                pass
