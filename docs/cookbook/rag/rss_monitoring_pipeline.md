# RSS Monitoring Pipeline

Use RSS monitoring for lightweight continuous ingestion of external updates.

```python
from agentic_assistants.pipelines.templates import create_rss_monitoring_pipeline

pipe = create_rss_monitoring_pipeline(
    feeds=["https://example.com/feed.xml"],
    collection="news",
    since_hours=24,
)
run = pipe.run()
print(run.success)
```

Enable deduplication to avoid repeated chunk insertions across polling intervals.

