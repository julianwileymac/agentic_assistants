# Quality Filters and Deduplication

Use quality and hash deduplication to reduce noisy vectors and storage bloat.

```python
from agentic_assistants.data.rag.ingestion_pipeline import IngestionConfig

cfg = IngestionConfig(
    min_quality_score=0.35,
    deduplicate=True,
)
```

Combine this with `content_hash` metadata and chunk-level quality annotations.

