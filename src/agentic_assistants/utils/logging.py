"""
Structured logging utilities for Agentic Assistants.

This module provides logging setup with OpenTelemetry correlation,
structured output, and configurable log levels.

Features:
- Structured JSON logging for machine parsing
- Rich console output for development
- OpenTelemetry trace context correlation
- Per-module verbosity configuration
- Log streaming via WebSocket for UI display
- Context managers for request/session tracing

Example:
    >>> from agentic_assistants.utils.logging import setup_logging, get_logger
    >>> setup_logging(level="DEBUG")
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing request", extra={"user_id": 123})
    
    >>> # With structured logging
    >>> from agentic_assistants.utils.logging import StructuredLogger
    >>> slogger = StructuredLogger(__name__)
    >>> slogger.info("Processing", user_id=123, action="chat")
"""

import json
import logging
import sys
import threading
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from rich.console import Console
from rich.logging import RichHandler


# Global console for rich output
console = Console()

# Cache for loggers
_loggers: dict[str, logging.Logger] = {}

# Module-specific verbosity levels
_module_levels: dict[str, int] = {}

# Log event subscribers for streaming
_log_subscribers: list[Callable[[dict], None]] = []

# Thread-local context
_context = threading.local()


# === JSON Formatter ===


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON for structured logging.
    
    Output includes:
    - timestamp: ISO format timestamp
    - level: Log level name
    - logger: Logger name
    - message: Log message
    - context: Any contextual data
    - trace: OpenTelemetry trace context if available
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add thread info
        log_data["thread"] = record.threadName
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["context"] = record.extra_data
        
        # Add log context from thread-local storage
        context = getattr(_context, "data", {})
        if context:
            log_data["context"] = {**context, **log_data.get("context", {})}
        
        # Add OpenTelemetry trace context if available
        trace_context = _get_trace_context()
        if trace_context:
            log_data["trace"] = trace_context
        
        return json.dumps(log_data)


class StructuredLogAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds structured data to log records.
    """
    
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        if self.extra:
            extra = {**self.extra, **extra}
        kwargs["extra"] = {"extra_data": extra}
        return msg, kwargs


# === Streaming Support ===


class StreamingHandler(logging.Handler):
    """
    Handler that streams log events to subscribers.
    
    Used for sending logs to WebSocket connections for UI display.
    """
    
    def emit(self, record: logging.LogRecord):
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            # Add extra data
            if hasattr(record, "extra_data"):
                log_entry["context"] = record.extra_data
            
            # Notify all subscribers
            for subscriber in _log_subscribers:
                try:
                    subscriber(log_entry)
                except Exception:
                    pass  # Don't let subscriber errors break logging
        except Exception:
            self.handleError(record)


def subscribe_to_logs(callback: Callable[[dict], None]) -> Callable[[], None]:
    """
    Subscribe to log events for streaming.
    
    Args:
        callback: Function to call with each log entry
    
    Returns:
        Unsubscribe function
    """
    _log_subscribers.append(callback)
    
    def unsubscribe():
        if callback in _log_subscribers:
            _log_subscribers.remove(callback)
    
    return unsubscribe


# === OpenTelemetry Integration ===


def _get_trace_context() -> Optional[dict]:
    """Get current OpenTelemetry trace context if available."""
    try:
        from opentelemetry import trace
        from opentelemetry.trace import get_current_span
        
        span = get_current_span()
        if span and span.get_span_context().is_valid:
            ctx = span.get_span_context()
            return {
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
            }
    except ImportError:
        pass
    except Exception:
        pass
    
    return None


def setup_otel_logging() -> None:
    """
    Set up OpenTelemetry logging integration.
    
    This adds trace context to log records and optionally
    exports logs to the configured OTLP endpoint.
    """
    try:
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        
        LoggingInstrumentor().instrument(set_logging_format=False)
    except ImportError:
        pass  # OpenTelemetry not installed


# === Main Setup Functions ===


def setup_logging(
    level: str = "DEBUG",
    enable_rich: bool = True,
    enable_json: bool = False,
    enable_streaming: bool = False,
    log_file: Optional[str] = None,
    module_levels: Optional[dict[str, str]] = None,
    enable_otel: bool = True,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_rich: Use rich handler for colorful console output
        enable_json: Use JSON formatting for structured logging
        enable_streaming: Enable log streaming for WebSocket subscribers
        log_file: Optional file path for file logging
        module_levels: Dict mapping module names to log levels
        enable_otel: Enable OpenTelemetry integration
    """
    global _module_levels
    
    log_level = getattr(logging, level.upper(), logging.DEBUG)

    # Store module-specific levels
    if module_levels:
        for module, mod_level in module_levels.items():
            _module_levels[module] = getattr(logging, mod_level.upper(), logging.DEBUG)

    # Create formatters
    detailed_format = "%(asctime)s | %(name)s | %(levelname)s | %(threadName)s | %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    if enable_json:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
    elif enable_rich:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(detailed_format))

    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        # Use JSON for file logging
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    
    # Add streaming handler if enabled
    if enable_streaming:
        streaming_handler = StreamingHandler()
        streaming_handler.setLevel(log_level)
        root_logger.addHandler(streaming_handler)

    # Configure third-party library logging
    _configure_library_logging()
    
    # Set up OpenTelemetry if enabled
    if enable_otel:
        setup_otel_logging()


def _configure_library_logging():
    """Configure logging levels for third-party libraries."""
    library_levels = {
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "urllib3": logging.WARNING,
        "openai": logging.WARNING,
        "mlflow": logging.INFO,
        "chromadb": logging.WARNING,
        "lancedb": logging.WARNING,
        "langchain": logging.INFO,
        "crewai": logging.INFO,
        "llama_index": logging.INFO,
    }
    
    for library, level in library_levels.items():
        logging.getLogger(library).setLevel(level)


def set_module_level(module: str, level: str) -> None:
    """
    Set the logging level for a specific module.
    
    Args:
        module: Module name (e.g., "agentic_assistants.server")
        level: Log level name
    """
    log_level = getattr(logging, level.upper(), logging.DEBUG)
    _module_levels[module] = log_level
    logging.getLogger(module).setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        
        # Apply module-specific level if configured
        for module_prefix, level in _module_levels.items():
            if name.startswith(module_prefix):
                logger.setLevel(level)
                break
        
        _loggers[name] = logger
    
    return _loggers[name]


# === Structured Logger ===


class StructuredLogger:
    """
    A logger that provides structured logging with keyword arguments.
    
    Example:
        >>> logger = StructuredLogger(__name__)
        >>> logger.info("User logged in", user_id=123, ip="192.168.1.1")
    """
    
    def __init__(self, name: str, **default_context):
        self._logger = get_logger(name)
        self._default_context = default_context
    
    def _log(self, level: int, message: str, **kwargs):
        extra = {**self._default_context, **kwargs}
        self._logger.log(level, message, extra={"extra_data": extra})
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        self._logger.exception(message, extra={"extra_data": {**self._default_context, **kwargs}})
    
    def with_context(self, **context) -> "StructuredLogger":
        """Create a new logger with additional default context."""
        return StructuredLogger(
            self._logger.name,
            **{**self._default_context, **context}
        )


# === Context Management ===


class LogContext:
    """
    Context manager for adding contextual information to log messages.
    
    Example:
        >>> with LogContext(request_id="abc123", user="john"):
        ...     logger.info("Processing request")
    """

    def __init__(self, **kwargs):
        self.new_context = kwargs
        self.old_context = {}

    def __enter__(self):
        self.old_context = getattr(_context, "data", {}).copy()
        new_data = {**self.old_context, **self.new_context}
        _context.data = new_data
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _context.data = self.old_context
        return False

    @classmethod
    def get_context(cls) -> dict:
        """Get the current logging context."""
        return getattr(_context, "data", {}).copy()
    
    @classmethod
    def set(cls, **kwargs) -> None:
        """Set context values without context manager."""
        current = getattr(_context, "data", {})
        _context.data = {**current, **kwargs}
    
    @classmethod
    def clear(cls) -> None:
        """Clear all context."""
        _context.data = {}


@contextmanager
def log_context(**kwargs):
    """
    Context manager shorthand for LogContext.
    
    Example:
        >>> with log_context(request_id="abc"):
        ...     do_something()
    """
    with LogContext(**kwargs) as ctx:
        yield ctx


def with_logging_context(**context_kwargs):
    """
    Decorator to add logging context to a function.
    
    Example:
        >>> @with_logging_context(component="auth")
        ... def authenticate(user_id):
        ...     logger.info("Authenticating")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with LogContext(**context_kwargs):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# === Performance Logging ===


class PerformanceLogger:
    """
    Logger for tracking performance metrics.
    
    Example:
        >>> perf = PerformanceLogger(__name__)
        >>> with perf.timer("database_query"):
        ...     result = db.query()
    """
    
    def __init__(self, name: str):
        self._logger = StructuredLogger(name)
    
    @contextmanager
    def timer(self, operation: str, **extra):
        """Time an operation and log the duration."""
        import time
        start = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self._logger.info(
                f"Operation completed: {operation}",
                operation=operation,
                duration_ms=round(duration_ms, 2),
                **extra
            )
    
    def log_metric(self, name: str, value: float, unit: str = "", **extra):
        """Log a metric value."""
        self._logger.info(
            f"Metric: {name}={value}{unit}",
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            **extra
        )


# === Audit Logging ===


class AuditLogger:
    """
    Logger for audit trail events.
    
    Tracks user actions, access events, and security-relevant operations.
    """
    
    def __init__(self, name: str = "audit"):
        self._logger = StructuredLogger(name)
    
    def log_access(self, resource: str, action: str, user_id: str, success: bool, **extra):
        """Log an access event."""
        self._logger.info(
            f"Access: {user_id} {action} {resource}",
            event_type="access",
            resource=resource,
            action=action,
            user_id=user_id,
            success=success,
            **extra
        )
    
    def log_action(self, action: str, user_id: str, target: Optional[str] = None, **extra):
        """Log a user action."""
        self._logger.info(
            f"Action: {user_id} performed {action}",
            event_type="action",
            action=action,
            user_id=user_id,
            target=target,
            **extra
        )
    
    def log_security(self, event: str, severity: str = "low", **extra):
        """Log a security event."""
        level = logging.WARNING if severity in ("medium", "high") else logging.INFO
        self._logger._log(
            level,
            f"Security: {event}",
            event_type="security",
            severity=severity,
            **extra
        )


# === File Logging Setup ===


def setup_file_logging(
    log_dir: Path,
    app_name: str = "agentic",
    rotate_size_mb: int = 10,
    backup_count: int = 5,
) -> None:
    """
    Set up file logging with rotation.
    
    Args:
        log_dir: Directory for log files
        app_name: Application name for log file prefix
        rotate_size_mb: Max size per log file in MB
        backup_count: Number of backup files to keep
    """
    from logging.handlers import RotatingFileHandler
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Main application log
    app_log = log_dir / f"{app_name}.log"
    app_handler = RotatingFileHandler(
        app_log,
        maxBytes=rotate_size_mb * 1024 * 1024,
        backupCount=backup_count,
    )
    app_handler.setFormatter(JSONFormatter())
    app_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(app_handler)
    
    # Error log (errors and above only)
    error_log = log_dir / f"{app_name}.error.log"
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=rotate_size_mb * 1024 * 1024,
        backupCount=backup_count,
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(error_handler)
    
    # Audit log
    audit_log = log_dir / f"{app_name}.audit.log"
    audit_handler = RotatingFileHandler(
        audit_log,
        maxBytes=rotate_size_mb * 1024 * 1024,
        backupCount=backup_count,
    )
    audit_handler.setFormatter(JSONFormatter())
    audit_handler.setLevel(logging.INFO)
    logging.getLogger("audit").addHandler(audit_handler)
