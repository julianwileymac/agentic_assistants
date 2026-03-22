"""Hybrid cache starter."""

from agentic_assistants.data.caching import CacheConfig, HybridCache


def main() -> None:
    cache = HybridCache(
        CacheConfig(
            backend="hybrid",
            l1_max_size=128,
            l1_ttl_seconds=120,
            l2_backend="redis",
        )
    )
    cache.set("q:auth", {"answer": "Authentication service is in src/..."}, ttl_seconds=600)
    print(cache.get("q:auth"))
    print(cache.get_tier_info())


if __name__ == "__main__":
    main()

