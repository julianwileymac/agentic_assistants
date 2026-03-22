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

if DAGSTER_AVAILABLE:

    @dg.success_hook
    def mlflow_success_hook(context: dg.HookContext):
        """Dagster hook that logs success to MLFlow on op completion."""
        logger.debug(f"Success hook fired for: {context.op.name}")
        _metrics.record_op(context.op.name, 0)  # duration not available in hook

    @dg.failure_hook
    def mlflow_failure_hook(context: dg.HookContext):
        """Dagster hook that logs failure to MLFlow on op failure."""
        logger.warning(f"Failure hook fired for: {context.op.name}")
        _metrics.record_op(context.op.name, 0)
