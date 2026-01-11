# Chunk: 2ebb5df1da68_2

- source: `src/agentic_assistants/data/telemetry.py`
- lines: 158-243
- chunk: 3/4

```
ion_name: Optional[str] = None,
    component: str = "data",
):
    """
    Decorator for tracing functions.
    
    Args:
        operation_name: Name for the operation (uses function name if None)
        component: Component name
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with trace_operation(op_name, component):
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with trace_operation(op_name, component):
                return await func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


# ============================================================================
# Logging Enhancements
# ============================================================================

class StructuredLogger:
    """
    Structured logger for data operations.
    
    Provides consistent logging with context and metrics.
    """
    
    def __init__(self, name: str, component: str = "data"):
        self.name = name
        self.component = component
        self._logger = get_logger(name)
    
    def info(self, message: str, **context):
        """Log info message with context."""
        self._log("info", message, context)
    
    def debug(self, message: str, **context):
        """Log debug message with context."""
        self._log("debug", message, context)
    
    def warning(self, message: str, **context):
        """Log warning message with context."""
        self._log("warning", message, context)
    
    def error(self, message: str, **context):
        """Log error message with context."""
        self._log("error", message, context)
        _metrics.increment(f"{self.component}.errors", tags={"name": self.name})
    
    def _log(self, level: str, message: str, context: Dict[str, Any]):
        """Internal logging method."""
        # Build structured message
        context_str = " ".join(f"{k}={v}" for k, v in context.items())
        full_message = f"[{self.component}] {message} {context_str}".strip()
        
        log_method = getattr(self._logger, level)
        log_method(full_message)
    
    def operation_start(self, operation: str, **context):
        """Log operation start."""
        self.info(f"Starting {operation}", operation=operation, **context)
    
    def operation_complete(self, operation: str, duration: float, **context):
        """Log operation completion."""
        self.info(
            f"Completed {operation}",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            **context
        )
```
