# Keyword Augmentation

Use keyword augmentation for better recall on sparse user queries.

```python
from agentic_assistants.data.rag.augmenters import KeywordAugmenter

augmenter = KeywordAugmenter(max_keywords=12)
chunk = augmenter.augment(chunk, {})
print(chunk.metadata["keywords"])
```

For local-first workflows, start with TF keywords and add LLM extraction only when needed.

