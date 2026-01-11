# Chunk: 2ebb5df1da68_3

- source: `src/agentic_assistants/data/telemetry.py`
- lines: 234-297
- chunk: 4/4

```

    def operation_complete(self, operation: str, duration: float, **context):
        """Log operation completion."""
        self.info(
            f"Completed {operation}",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            **context
        )
        _metrics.record(f"{self.component}.operation.duration", duration, {"operation": operation})
    
    def operation_failed(self, operation: str, error: str, **context):
        """Log operation failure."""
        self.error(f"Failed {operation}: {error}", operation=operation, **context)


def get_data_logger(name: str, component: str = "data") -> StructuredLogger:
    """Get a structured logger for data operations."""
    return StructuredLogger(name, component)


# ============================================================================
# Component-specific loggers and tracers
# ============================================================================

# Catalog operations
catalog_logger = get_data_logger("catalog", "catalog")

def trace_catalog_operation(operation: str):
    """Trace a catalog operation."""
    return trace_operation(operation, "catalog")


# Cache operations
cache_logger = get_data_logger("cache", "cache")

def trace_cache_operation(operation: str):
    """Trace a cache operation."""
    return trace_operation(operation, "cache")


# Feature store operations
feature_logger = get_data_logger("features", "features")

def trace_feature_operation(operation: str):
    """Trace a feature store operation."""
    return trace_operation(operation, "features")


# Ingestion operations
ingestion_logger = get_data_logger("ingestion", "ingestion")

def trace_ingestion_operation(operation: str):
    """Trace an ingestion operation."""
    return trace_operation(operation, "ingestion")


# Knowledge base operations
kb_logger = get_data_logger("knowledge", "knowledge")

def trace_kb_operation(operation: str):
    """Trace a knowledge base operation."""
    return trace_operation(operation, "knowledge")
```
