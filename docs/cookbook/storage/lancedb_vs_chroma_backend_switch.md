# LanceDB vs Chroma Backend Switch

Use this recipe to switch vector backends without changing higher-level retrieval logic.

```python
from agentic_assistants.vectordb.base import VectorStore

lance = VectorStore.create(backend="lancedb")
chroma = VectorStore.create(backend="chroma")
```

Benchmark both on:
- indexing throughput
- query latency
- metadata filtering behavior

