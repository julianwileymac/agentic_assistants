# Simple Local RAG

Use this when you need a local retrieval + generation baseline with minimal moving parts.

```python
from agentic_assistants.patterns.rag_pattern import RAGPattern
from agentic_assistants.vectordb.base import VectorStore

store = VectorStore.create(backend="lancedb")
rag = RAGPattern(vector_store=store, collection="docs", top_k=5)
result = rag.query("How is indexing implemented?")
print(result.output)
```

Keep the first baseline simple, then add reranking and augmentation once quality metrics exist.

