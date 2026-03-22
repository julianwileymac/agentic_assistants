# Metadata Augmentation

Use metadata augmentation to add source provenance and chunk diagnostics.

```python
from agentic_assistants.data.rag.augmenters import MetadataAugmenter

augmenter = MetadataAugmenter(include_hash=True, include_stats=True)
chunk = augmenter.augment(chunk, {"source": "manual.md", "source_type": "file"})
```

Common fields: `content_hash`, `char_count`, `word_count`, `ingested_at`.

