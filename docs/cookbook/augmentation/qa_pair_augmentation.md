# QA Pair Augmentation

Generate question metadata to create alternative retrieval entry points.

```python
from agentic_assistants.data.rag.augmenters import QAGenerationAugmenter

qa = QAGenerationAugmenter(num_questions=3, llm_fn=my_llm_fn)
chunk = qa.augment(chunk, {})
print(chunk.metadata["questions"])
```

Store generated questions in metadata and include them in reindexing decisions.

