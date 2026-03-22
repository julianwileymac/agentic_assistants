# Artifacts and Lineage

Persist chunk artifacts for replay, inspection, and provenance.

```python
from agentic_assistants.data.rag.ingestion_pipeline import IngestionConfig, IngestionPipeline

cfg = IngestionConfig(store_as_files=True, artifacts_dir="./data/artifacts")
pipeline = IngestionPipeline(config=cfg)
result = pipeline.ingest(source="notes.md", source_type="file", collection="docs")
print(result.file_path)
```

Store artifact paths in metadata so answers can reference original evidence.

