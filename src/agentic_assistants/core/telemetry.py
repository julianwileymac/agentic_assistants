"""
OpenTelemetry tracing and metrics integration.

This module provides:
- Distributed tracing across agent calls
- Metrics collection (latency, token counts, etc.)
- Log correlation with trace IDs

Example:
    >>> from agentic_assistants import AgenticConfig
    >>> from agentic_assistants.core import TelemetryManager, get_tracer
    >>> 
    >>> config = AgenticConfig(telemetry_enabled=True)
    >>> telemetry = TelemetryManager(config)
    >>> telemetry.initialize()
    >>> 
    >>> tracer = get_tracer("my-agent")
    >>> with tracer.start_as_current_span("agent-task") as span:
    ...     span.set_attribute("model", "llama3.2")
    ...     result = run_agent()
"""

import functools
import socket
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Global telemetry manager instance
_telemetry_manager: Optional["TelemetryManager"] = None


class TelemetryManager:
    """
    OpenTelemetry observability manager.
    
    This class manages the OpenTelemetry SDK configuration and provides
    utilities for creating spans, recording metrics, and correlating logs.
    
    Attributes:
        config: Agentic configuration instance
        enabled: Whether telemetry is enabled
        service_name: Service name for traces
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the telemetry manager.
        
        Args:
            config: Configuration instance. If None, uses default config.
        """
        self.config = config or AgenticConfig()
        self.enabled = self.config.telemetry_enabled
        self.service_name = self.config.telemetry.service_name
        self._tracer = None
        self._meter = None
        self._initialized = False

        # Register as global manager
        global _telemetry_manager
        _telemetry_manager = self

    @staticmethod
    def _endpoint_reachable(endpoint: str, timeout: float = 1.0) -> bool:
        """Check if an OTLP gRPC endpoint is reachable via TCP."""
        parsed = urlparse(endpoint if "://" in endpoint else f"http://{endpoint}")
        host = parsed.hostname or "localhost"
        port = parsed.port or 4317
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def _resolve_span_exporter(self, resource):
        """
        Resolve the best available span exporter using a tiered strategy:
          1. Kubernetes OTLP collector (if K8s enabled)
          2. Configured / local OTLP collector (Docker or standalone)
          3. File-based OTLP JSON exporter (offline fallback)

        Returns:
            Tuple of (exporter, description_string)
        """
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        candidates: list[tuple[str, str]] = []

        if getattr(self.config, "kubernetes", None) and self.config.kubernetes.enabled:
            candidates.append(("http://otel-collector:4317", "K8s OTLP collector"))

        configured = self.config.telemetry.exporter_otlp_endpoint
        candidates.append((configured, f"configured endpoint ({configured})"))

        for endpoint, label in candidates:
            if self._endpoint_reachable(endpoint):
                exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
                return exporter, label

        if self.config.telemetry.fallback_to_file:
            from agentic_assistants.observability.trace_store import FileSpanExporter
            export_dir = Path(self.config.telemetry.file_export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            exporter = FileSpanExporter(export_dir)
            return exporter, f"file exporter ({export_dir})"

        return None, "none"

    def initialize(self) -> None:
        """
        Initialize OpenTelemetry SDK with the best available exporter.
        
        Uses a tiered backend strategy:
        1. Kubernetes OTLP collector (when K8s is enabled and reachable)
        2. Local / Docker OTLP collector (configured endpoint)
        3. File-based OTLP JSON exporter (offline fallback)
        """
        if self._initialized or not self.enabled:
            return

        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

            resource = Resource.create(
                {
                    "service.name": self.service_name,
                    "service.version": "0.1.0",
                    "deployment.environment": "development",
                }
            )

            trace_provider = TracerProvider(resource=resource)

            span_exporter, exporter_label = self._resolve_span_exporter(resource)
            if span_exporter is None:
                logger.warning("No OTLP endpoint reachable and file fallback disabled. Telemetry disabled.")
                self.enabled = False
                return

            trace_provider.add_span_processor(BatchSpanProcessor(span_exporter))
            trace.set_tracer_provider(trace_provider)

            # Metrics: best-effort OTLP, silently skip if unreachable
            try:
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                metric_endpoint = self.config.telemetry.exporter_otlp_endpoint
                if self._endpoint_reachable(metric_endpoint):
                    metric_reader = PeriodicExportingMetricReader(
                        OTLPMetricExporter(endpoint=metric_endpoint, insecure=True),
                        export_interval_millis=60000,
                    )
                    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
                else:
                    meter_provider = MeterProvider(resource=resource)
            except Exception:
                meter_provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(meter_provider)

            self._tracer = trace.get_tracer(self.service_name)
            self._meter = metrics.get_meter(self.service_name)

            self._initialized = True
            logger.info(
                f"OpenTelemetry initialized - exporter: {exporter_label}, "
                f"service: {self.service_name}"
            )

        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry: {e}. Telemetry disabled.")
            self.enabled = False

    def get_tracer(self, name: Optional[str] = None):
        """
        Get a tracer instance.
        
        Args:
            name: Optional tracer name (uses service name if None)
        
        Returns:
            Tracer instance or NoOpTracer if disabled
        """
        if not self.enabled:
            return _NoOpTracer()

        if not self._initialized:
            self.initialize()

        if self._tracer:
            return self._tracer

        from opentelemetry import trace

        return trace.get_tracer(name or self.service_name)

    def get_meter(self, name: Optional[str] = None):
        """
        Get a meter instance for recording metrics.
        
        Args:
            name: Optional meter name (uses service name if None)
        
        Returns:
            Meter instance or NoOpMeter if disabled
        """
        if not self.enabled:
            return _NoOpMeter()

        if not self._initialized:
            self.initialize()

        if self._meter:
            return self._meter

        from opentelemetry import metrics

        return metrics.get_meter(name or self.service_name)

    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, Any]] = None,
        kind: Optional[Any] = None,
    ):
        """
        Create a span as a context manager.
        
        Args:
            name: Span name
            attributes: Optional attributes to set on the span
            kind: Span kind (CLIENT, SERVER, INTERNAL, etc.).
                  Defaults to SpanKind.INTERNAL when None.
        
        Yields:
            The span instance
        
        Example:
            >>> with telemetry.span("process-request", {"user_id": 123}) as span:
            ...     result = process()
            ...     span.set_attribute("result_size", len(result))
        """
        if not self.enabled:
            yield _NoOpSpan()
            return

        from opentelemetry.trace import SpanKind
        resolved_kind = kind if kind is not None else SpanKind.INTERNAL

        tracer = self.get_tracer()
        with tracer.start_as_current_span(name, kind=resolved_kind) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            yield span

    def record_agent_metrics(
        self,
        agent_name: str,
        model: str,
        duration_seconds: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        success: bool = True,
    ) -> None:
        """
        Record standardized agent metrics.
        
        Args:
            agent_name: Name of the agent
            model: Model used
            duration_seconds: Execution duration
            tokens_input: Input token count
            tokens_output: Output token count
            success: Whether the operation succeeded
        """
        if not self.enabled:
            return

        try:
            meter = self.get_meter()

            # Get or create counters and histograms
            duration_histogram = meter.create_histogram(
                "agent.duration",
                description="Agent execution duration in seconds",
                unit="s",
            )
            token_counter = meter.create_counter(
                "agent.tokens",
                description="Token usage by agents",
                unit="tokens",
            )
            request_counter = meter.create_counter(
                "agent.requests",
                description="Number of agent requests",
                unit="1",
            )

            # Record metrics with attributes
            attributes = {
                "agent.name": agent_name,
                "model": model,
                "success": str(success).lower(),
            }

            duration_histogram.record(duration_seconds, attributes)
            token_counter.add(tokens_input, {**attributes, "direction": "input"})
            token_counter.add(tokens_output, {**attributes, "direction": "output"})
            request_counter.add(1, attributes)

        except Exception as e:
            logger.warning(f"Failed to record agent metrics: {e}")

    def shutdown(self) -> None:
        """Gracefully shutdown telemetry exporters."""
        if not self._initialized:
            return

        try:
            from opentelemetry import trace, metrics

            trace_provider = trace.get_tracer_provider()
            if hasattr(trace_provider, "shutdown"):
                trace_provider.shutdown()

            meter_provider = metrics.get_meter_provider()
            if hasattr(meter_provider, "shutdown"):
                meter_provider.shutdown()

            logger.info("OpenTelemetry shutdown complete")

        except Exception as e:
            logger.warning(f"Error during telemetry shutdown: {e}")


class _NoOpSpan:
    """No-operation span for when telemetry is disabled."""

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        pass

    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        pass

    def record_exception(self, exception: Exception) -> None:
        pass

    def set_status(self, status: Any) -> None:
        pass


class _NoOpTracer:
    """No-operation tracer for when telemetry is disabled."""

    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        yield _NoOpSpan()

    def start_span(self, name: str, **kwargs):
        return _NoOpSpan()


class _NoOpMeter:
    """No-operation meter for when telemetry is disabled."""

    def create_counter(self, name: str, **kwargs):
        return _NoOpCounter()

    def create_histogram(self, name: str, **kwargs):
        return _NoOpHistogram()

    def create_up_down_counter(self, name: str, **kwargs):
        return _NoOpCounter()


class _NoOpCounter:
    """No-operation counter."""

    def add(self, amount: int, attributes: Optional[dict] = None) -> None:
        pass


class _NoOpHistogram:
    """No-operation histogram."""

    def record(self, value: float, attributes: Optional[dict] = None) -> None:
        pass


def get_tracer(name: Optional[str] = None):
    """
    Get a tracer instance from the global telemetry manager.
    
    Args:
        name: Optional tracer name
    
    Returns:
        Tracer instance
    """
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    return _telemetry_manager.get_tracer(name)


def get_meter(name: Optional[str] = None):
    """
    Get a meter instance from the global telemetry manager.
    
    Args:
        name: Optional meter name
    
    Returns:
        Meter instance
    """
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    return _telemetry_manager.get_meter(name)


def trace_function(
    span_name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
    record_args: bool = False,
) -> Callable:
    """
    Decorator to trace a function execution.
    
    Args:
        span_name: Name for the span (uses function name if None)
        attributes: Static attributes to add to the span
        record_args: Whether to record function arguments as attributes
    
    Returns:
        Decorated function
    
    Example:
        >>> @trace_function(attributes={"component": "research"})
        >>> def research_topic(topic: str):
        ...     return find_information(topic)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            span_attrs = attributes.copy() if attributes else {}

            if record_args:
                for i, arg in enumerate(args):
                    span_attrs[f"arg.{i}"] = str(arg)[:100]
                for key, value in kwargs.items():
                    span_attrs[f"kwarg.{key}"] = str(value)[:100]

            global _telemetry_manager
            if _telemetry_manager is None:
                _telemetry_manager = TelemetryManager()

            with _telemetry_manager.span(name, attributes=span_attrs) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_seconds", duration)

        return wrapper

    return decorator

