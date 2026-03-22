# LLM Abstractive Augmentation

Use LLM augmentation when compressed summaries and generated prompts materially improve retrieval quality.

```python
from agentic_assistants.data.rag.augmenters import SummaryAugmenter

abstractive = SummaryAugmenter(use_llm=True, llm_fn=my_llm_fn, max_length=200)
chunk = abstractive.augment(chunk, {})
```

Guardrails:
- enforce summary length limits
- log failures and keep original content fallback
- track augmentation cost and latency

