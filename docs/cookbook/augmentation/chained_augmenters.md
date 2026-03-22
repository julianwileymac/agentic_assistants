# Chained Augmenters

Compose augmenters in a deterministic order for reproducible enrichment.

```python
from agentic_assistants.data.rag.augmenters import (
    ChainedAugmenter,
    MetadataAugmenter,
    KeywordAugmenter,
    SummaryAugmenter,
)

augment = ChainedAugmenter([MetadataAugmenter(), KeywordAugmenter(), SummaryAugmenter()])
chunk = augment.augment(chunk, {"source": "design.md"})
```

Recommended order: metadata -> lexical extraction -> semantic/LLM transforms.

