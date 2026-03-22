# Scoped Retrieval

Use scoped retrieval when global knowledge should be shared but project data must stay isolated.

```python
from agentic_assistants.vectordb.scoped_store import ScopedVectorStore

store = ScopedVectorStore(project_id="proj-abc")
results = store.search(
    "authentication design",
    collection="knowledge",
    include_global=True,
    include_parent_scopes=True,
)
```

Recommended policy:
- write project-specific documents to project scope
- write reusable references to global scope
- query with `include_global=True` for fallback behavior

