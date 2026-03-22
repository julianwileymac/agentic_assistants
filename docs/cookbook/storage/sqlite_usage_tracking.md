# SQLite Usage Tracking

Use `UsageTracker` to persist application telemetry without external services.

```python
from agentic_assistants.observability.usage_tracker import UsageTracker

tracker = UsageTracker()
tracker.track_rag_query(
    knowledge_base="docs",
    query="How do templates work?",
    num_results=5,
    duration_ms=12.4,
)
```

SQLite storage is ideal for local-first development and reproducible experiments.

