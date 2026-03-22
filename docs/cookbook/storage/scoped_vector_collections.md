# Scoped Vector Collections

Use scoped collections to prevent project cross-contamination.

```python
from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
from agentic_assistants.vectordb.base import Document

store = ScopedVectorStore(project_id="project-x")
store.add(Document(id="a", content="project note"), collection="notes")
```

Collection names are automatically namespaced by scope and identifiers.

