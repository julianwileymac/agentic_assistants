# Chunk: 2ebb5df1da68_1

- source: `src/agentic_assistants/data/telemetry.py`
- lines: 75-169
- chunk: 2/4

```
alues[int(n * 0.95)] if n >= 20 else sorted_values[-1],
            "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1],
        }
    
    def export(self) -> Dict[str, Any]:
        """Export all metrics."""
        return {
            "counters": dict(self._counters),
            "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
            "gauges": dict(self._gauges),
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._histograms.clear()
        self._gauges.clear()


# Global metrics instance
_metrics = DataMetrics()


def get_metrics() -> DataMetrics:
    """Get the global metrics collector."""
    return _metrics


# ============================================================================
# Tracing
# ============================================================================

@contextmanager
def trace_operation(
    operation_name: str,
    component: str = "data",
    tags: Optional[Dict[str, str]] = None,
):
    """
    Context manager for tracing operations.
    
    Args:
        operation_name: Name of the operation
        component: Component name
        tags: Additional tags
    """
    start_time = time.time()
    tags = tags or {}
    tags["component"] = component
    
    # Start trace
    try:
        from agentic_assistants.core.telemetry import tracer
        
        with tracer.start_as_current_span(operation_name) as span:
            for key, value in tags.items():
                span.set_attribute(key, value)
            
            try:
                yield span
                span.set_attribute("success", True)
            except Exception as e:
                span.set_attribute("success", False)
                span.set_attribute("error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration_ms", duration * 1000)
                _metrics.record(f"{component}.{operation_name}.duration", duration, tags)
                _metrics.increment(f"{component}.{operation_name}.count", tags=tags)
                
    except ImportError:
        # Fallback without OpenTelemetry
        try:
            yield None
        finally:
            duration = time.time() - start_time
            _metrics.record(f"{component}.{operation_name}.duration", duration, tags)
            _metrics.increment(f"{component}.{operation_name}.count", tags=tags)


def trace_function(
    operation_name: Optional[str] = None,
    component: str = "data",
):
    """
    Decorator for tracing functions.
    
    Args:
        operation_name: Name for the operation (uses function name if None)
        component: Component name
    """
    def decorator(func: Callable) -> Callable:
```
