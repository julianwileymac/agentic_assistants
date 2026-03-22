# Summary Augmentation

Attach compact summaries to each chunk for faster preview and reranking.

```python
from agentic_assistants.data.rag.augmenters import SummaryAugmenter

summary = SummaryAugmenter(max_length=180, use_llm=False)
chunk = summary.augment(chunk, {})
print(chunk.metadata["summary"])
```

Use extractive summaries first; enable LLM mode for abstractive compression.

