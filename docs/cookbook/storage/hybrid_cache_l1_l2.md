# Hybrid Cache L1/L2

Use the hybrid cache when you need low latency locally and shared cache state across processes.

```python
from agentic_assistants.data.caching import CacheConfig, HybridCache

cache = HybridCache(CacheConfig(backend="hybrid", l2_backend="redis"))
cache.set("query:auth", {"answer": "..."}, ttl_seconds=3600)
print(cache.get("query:auth"))
```

L1 is local memory, L2 is Redis. Reads promote values from L2 to L1.

