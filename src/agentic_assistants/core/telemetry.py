"""
OpenTelemetry tracing and metrics integration.

This module provides:
- Distributed tracing across agent calls
- Metrics collection (latency, token counts, etc.)
- Log correlation with trace IDs
- Verbose debugging mode

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
import logging
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Global telemetry manager instance
_telemetry_manager: Optional["TelemetryManager"] = None


class TraceCorrelationHandler(logging.Handler):
    """
    Custom logging handler that adds trace context to log records.
    
    This enables log correlation with distributed traces by injecting
    trace_id and span_id into each log record.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trace_api = None
    
    def _get_trace_api(self):
        if self._trace_api is None:
            try:
                from opentelemetry import trace
                self._trace_api = trace
            except ImportError:
                pass
        return self._trace_api
    
    def emit(self, record: logging.LogRecord) -> None:
        trace_api = self._get_trace_api()
        if trace_api is None:
            return
        
        span = trace_api.get_current_span()
        if span and span.is_recording():
            ctx = span.get_span_context()
            record.trace_id = format(ctx.trace_id, '032x')
            record.span_id = format(ctx.span_id, '016x')
            record.trace_flags = ctx.trace_flags
        else:
            record.trace_id = None
            record.span_id = None
            record.trace_flags = None


class VerboseSpanLogger:
    """
    Helper class for verbose span logging and event recording.
    """
    
    def __init__(self, span: Any, verbose: bool = False):
        self.span = span
        self.verbose = verbose
        self._start_time = time.time()
    
    def log_event(self, name: str, attributes: Optional[dict] = None) -> None:
        """Add an event to the span with timestamp."""
        if self.span is None:
            return
        try:
            event_attrs = {"timestamp": datetime.now().isoformat()}
            if attributes:
                event_attrs.update({k: str(v)[:1000] for k, v in attributes.items()})
            self.span.add_event(name, attributes=event_attrs)
            if self.verbose:
                logger.debug(f"Span event: {name} - {event_attrs}")
        except Exception:
            pass
    
    def log_input(self, input_data: Any, truncate: int = 500) -> None:
        """Log input data as span event."""
        input_str = str(input_data)[:truncate]
        self.log_event("input_received", {"input": input_str, "length": len(str(input_data))})
        self.span.set_attribute("input.preview", input_str)
    
    def log_output(self, output_data: Any, truncate: int = 500) -> None:
        """Log output data as span event."""
        output_str = str(output_data)[:truncate]
        self.log_event("output_generated", {"output": output_str, "length": len(str(output_data))})
        self.span.set_attribute("output.preview", output_str)
    
    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        temperature: float = 0.0,
    ) -> None:
        """Log LLM call details."""
        self.span.set_attribute("llm.model", model)
        self.span.set_attribute("llm.prompt_tokens", prompt_tokens)
        self.span.set_attribute("llm.completion_tokens", completion_tokens)
        self.span.set_attribute("llm.total_tokens", prompt_tokens + completion_tokens)
        self.span.set_attribute("llm.temperature", temperature)
        self.log_event("llm_call", {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        })
    
    def log_error(self, error: Exception, include_traceback: bool = True) -> None:
        """Log error with full details."""
        self.span.set_attribute("error", True)
        self.span.set_attribute("error.type", type(error).__name__)
        self.span.set_attribute("error.message", str(error))
        
        if include_traceback:
            tb = traceback.format_exc()
            self.span.set_attribute("error.traceback", tb[:2000])
        
        try:
            self.span.record_exception(error)
        except Exception:
            pass
        
        self.log_event("error_occurred", {
            "type": type(error).__name__,
            "message": str(error)
        })
    
    def finalize(self, success: bool = True) -> None:
        """Finalize span with duration and status."""
        duration = time.time() - self._start_time
        self.span.set_attribute("duration_seconds", duration)
        self.span.set_attribute("success", success)
        self.log_event("completed", {"success": success, "duration_seconds": duration})


class TelemetryManager:
    """
    OpenTelemetry observability manager.
    
    This class manages the OpenTelemetry SDK configuration and provides
    utilities for creating spans, recording metrics, and correlating logs.
    
    Attributes:
        config: Agentic configuration instance
        enabled: Whether telemetry is enabled
        service_name: Service name for traces
        verbose: Enable verbose span logging
    """

    def __init__(self, config: Optional[AgenticConfig] = None, verbose: bool = False):
        """
        Initialize the telemetry manager.
        
        Args:
            config: Configuration instance. If None, uses default config.
            verbose: Enable verbose span logging for debugging
        """
        self.config = config or AgenticConfig()
        self.enabled = self.config.telemetry_enabled
        self.service_name = self.config.telemetry.service_name
        self.verbose = verbose
        self._tracer = None
        self._meter = None
        self._initialized = False
        
        # Metric instruments
        self._duration_histogram = None
        self._token_counter = None
        self._request_counter = None
        self._error_counter = None

        # Register as global manager
        global _telemetry_manager
        _telemetry_manager = self

    def initialize(self) -> None:
        """
        Initialize OpenTelemetry SDK with configured exporters.
        
        This sets up:
        - Trace provider with OTLP exporter
        - Meter provider for metrics
        - Log record processor for log correlation
        - Pre-created metric instruments for common use cases
        """
        if self._initialized or not self.enabled:
            return

        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

            # Create resource with service information
            resource = Resource.create(
                {
                    "service.name": self.service_name,
                    "service.version": "0.1.0",
                    "deployment.environment": "development",
                }
            )

            # Set up trace provider
            trace_provider = TracerProvider(resource=resource)
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.telemetry.exporter_otlp_endpoint,
                insecure=True,
            )
            trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            trace.set_tracer_provider(trace_provider)

            # Set up meter provider
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=self.config.telemetry.exporter_otlp_endpoint,
                    insecure=True,
                ),
                export_interval_millis=60000,
            )
            meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)

            # Store references
            self._tracer = trace.get_tracer(self.service_name)
            self._meter = metrics.get_meter(self.service_name)
            
            # Pre-create common metric instruments
            self._create_metric_instruments()
            
            # Set up log correlation
            self._setup_log_correlation()

            self._initialized = True
            logger.info(
                f"OpenTelemetry initialized - endpoint: {self.config.telemetry.exporter_otlp_endpoint}, "
                f"service: {self.service_name}, verbose: {self.verbose}"
            )

        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry: {e}. Telemetry disabled.")
            self.enabled = False
    
    def _create_metric_instruments(self) -> None:
        """Create commonly used metric instruments."""
        if self._meter is None:
            return
        
        self._duration_histogram = self._meter.create_histogram(
            "agent.duration",
            description="Agent execution duration in seconds",
            unit="s",
        )
        self._token_counter = self._meter.create_counter(
            "agent.tokens",
            description="Token usage by agents",
            unit="tokens",
        )
        self._request_counter = self._meter.create_counter(
            "agent.requests",
            description="Number of agent requests",
            unit="1",
        )
        self._error_counter = self._meter.create_counter(
            "agent.errors",
            description="Number of agent errors",
            unit="1",
        )
    
    def _setup_log_correlation(self) -> None:
        """Set up log correlation with traces."""
        # Add trace correlation handler to root logger
        correlation_handler = TraceCorrelationHandler()
        correlation_handler.setLevel(logging.DEBUG)
        
        # Create a formatter that includes trace context
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[trace_id=%(trace_id)s span_id=%(span_id)s] - %(message)s'
        )
        correlation_handler.setFormatter(formatter)
        
        # Add to agentic_assistants logger
        agentic_logger = logging.getLogger("agentic_assistants")
        agentic_logger.addHandler(correlation_handler)

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
        record_exception: bool = True,
    ):
        """
        Create a span as a context manager.
        
        Args:
            name: Span name
            attributes: Optional attributes to set on the span
            kind: Span kind (CLIENT, SERVER, INTERNAL, etc.)
            record_exception: Whether to record exceptions automatically
        
        Yields:
            VerboseSpanLogger wrapping the span instance
        
        Example:
            >>> with telemetry.span("process-request", {"user_id": 123}) as span:
            ...     span.log_input(request_data)
            ...     result = process()
            ...     span.log_output(result)
        """
        if not self.enabled:
            yield VerboseSpanLogger(_NoOpSpan(), self.verbose)
            return

        tracer = self.get_tracer()
        with tracer.start_as_current_span(name, kind=kind, record_exception=record_exception) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value) if not isinstance(value, (bool, int, float)) else value)
            
            span.set_attribute("span.start_time", datetime.now().isoformat())
            span_logger = VerboseSpanLogger(span, self.verbose)
            span_logger.log_event("started", {"name": name})
            
            try:
                yield span_logger
                span_logger.finalize(success=True)
            except Exception as e:
                span_logger.log_error(e)
                span_logger.finalize(success=False)
                raise

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
            # Record metrics with attributes
            attributes = {
                "agent.name": agent_name,
                "model": model,
                "success": str(success).lower(),
            }

            if self._duration_histogram:
                self._duration_histogram.record(duration_seconds, attributes)
            if self._token_counter:
                self._token_counter.add(tokens_input, {**attributes, "direction": "input"})
                self._token_counter.add(tokens_output, {**attributes, "direction": "output"})
            if self._request_counter:
                self._request_counter.add(1, attributes)
            if not success and self._error_counter:
                self._error_counter.add(1, attributes)
            
            if self.verbose:
                logger.debug(
                    f"Recorded metrics for {agent_name}: duration={duration_seconds:.3f}s, "
                    f"tokens_in={tokens_input}, tokens_out={tokens_output}, success={success}"
                )

        except Exception as e:
            logger.warning(f"Failed to record agent metrics: {e}")
    
    def record_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float,
        error: Optional[str] = None,
    ) -> None:
        """
        Record HTTP request metrics.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_seconds: Request duration
            error: Optional error message
        """
        if not self.enabled:
            return
        
        try:
            meter = self.get_meter()
            
            http_duration = meter.create_histogram(
                "http.server.duration",
                description="HTTP server request duration",
                unit="s",
            )
            
            attributes = {
                "http.method": method,
                "http.route": path,
                "http.status_code": status_code,
            }
            
            http_duration.record(duration_seconds, attributes)
            
            if error and self._error_counter:
                self._error_counter.add(1, {**attributes, "error.type": "http"})
        
        except Exception as e:
            logger.warning(f"Failed to record HTTP metrics: {e}")

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
    
    def is_recording(self) -> bool:
        return False


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
    record_result: bool = False,
) -> Callable:
    """
    Decorator to trace a function execution.
    
    Args:
        span_name: Name for the span (uses function name if None)
        attributes: Static attributes to add to the span
        record_args: Whether to record function arguments as attributes
        record_result: Whether to record function result
    
    Returns:
        Decorated function
    
    Example:
        >>> @trace_function(attributes={"component": "research"}, record_args=True)
        >>> def research_topic(topic: str):
        ...     return find_information(topic)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            span_attrs = attributes.copy() if attributes else {}
            span_attrs["function.name"] = func.__name__
            span_attrs["function.module"] = func.__module__

            global _telemetry_manager
            if _telemetry_manager is None:
                _telemetry_manager = TelemetryManager()

            with _telemetry_manager.span(name, attributes=span_attrs) as span_logger:
                if record_args:
                    args_str = ", ".join(str(a)[:100] for a in args)
                    kwargs_str = ", ".join(f"{k}={v!r}"[:100] for k, v in kwargs.items())
                    span_logger.log_event("function_args", {
                        "args": args_str,
                        "kwargs": kwargs_str,
                    })

                try:
                    result = func(*args, **kwargs)
                    
                    if record_result:
                        span_logger.log_output(result)
                    
                    return result
                except Exception as e:
                    span_logger.log_error(e)
                    raise

        return wrapper

    return decorator


def trace_async_function(
    span_name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
    record_args: bool = False,
    record_result: bool = False,
) -> Callable:
    """
    Decorator to trace an async function execution.
    
    Same as trace_function but for async functions.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            span_attrs = attributes.copy() if attributes else {}
            span_attrs["function.name"] = func.__name__
            span_attrs["function.module"] = func.__module__
            span_attrs["async"] = True

            global _telemetry_manager
            if _telemetry_manager is None:
                _telemetry_manager = TelemetryManager()

            with _telemetry_manager.span(name, attributes=span_attrs) as span_logger:
                if record_args:
                    args_str = ", ".join(str(a)[:100] for a in args)
                    kwargs_str = ", ".join(f"{k}={v!r}"[:100] for k, v in kwargs.items())
                    span_logger.log_event("function_args", {
                        "args": args_str,
                        "kwargs": kwargs_str,
                    })

                try:
                    result = await func(*args, **kwargs)
                    
                    if record_result:
                        span_logger.log_output(result)
                    
                    return result
                except Exception as e:
                    span_logger.log_error(e)
                    raise

        return wrapper

    return decorator
