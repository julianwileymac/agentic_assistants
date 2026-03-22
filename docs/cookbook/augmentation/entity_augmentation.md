# Entity Augmentation

Use entity extraction for structured filters and analytics.

```python
from agentic_assistants.data.rag.augmenters import EntityAugmenter

augmenter = EntityAugmenter(extract_patterns=True, use_ner=False)
chunk = augmenter.augment(chunk, {})
print(chunk.metadata["entities"])
```

Entity metadata helps combine semantic retrieval with exact-value filtering.

