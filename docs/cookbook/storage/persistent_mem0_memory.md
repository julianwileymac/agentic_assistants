# Persistent mem0 Memory

Use mem0 memory to preserve assistant context and preferences.

```python
from agentic_assistants.memory import get_memory_store

mem = get_memory_store(backend="mem0", user_id="julian")
mem.add_memory("User prefers short responses", metadata={"type": "preference"})
hits = mem.search_memories("response style", limit=5)
print(hits.total)
```

This complements retrieval stores by preserving interaction history, not just documents.

