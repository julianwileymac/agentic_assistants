# RAG Evaluation Loop

Use a fixed question set and evaluate retrieval before tuning prompts.

```python
queries = [
    "How do I index a folder?",
    "How do I sync trace files?",
]

for q in queries:
    results = store.search(q, collection="docs", top_k=5)
    print(q, len(results), [r.score for r in results[:3]])
```

Track:
- retrieval hit count
- top result score distribution
- answer groundedness against returned context

