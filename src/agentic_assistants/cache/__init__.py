"""
Cache module for Agentic Assistants.

This module provides caching functionality with Redis support,
including solution caching for reusable agent outputs and
workflow state management.

Example:
    >>> from agentic_assistants.cache import RedisCache, SolutionCache
    >>> 
    >>> # Basic cache operations
    >>> cache = RedisCache()
    >>> cache.set("key", {"data": "value"}, ttl=3600)
    >>> data = cache.get("key")
    >>> 
    >>> # Solution caching
    >>> solutions = SolutionCache()
    >>> solutions.store_solution("parse-json", solution_data, tags=["json", "parsing"])
    >>> cached = solutions.get_solution("parse-json")
"""

from agentic_assistants.cache.redis_cache import (
    RedisCache,
    CacheConfig,
    CacheEntry,
)
from agentic_assistants.cache.solution_store import (
    SolutionCache,
    Solution,
    SolutionType,
    WorkflowState,
)

__all__ = [
    # Redis cache
    "RedisCache",
    "CacheConfig",
    "CacheEntry",
    # Solution store
    "SolutionCache",
    "Solution",
    "SolutionType",
    "WorkflowState",
]


# Global cache instance
_cache: RedisCache = None
_solution_cache: SolutionCache = None


def get_cache(config: CacheConfig = None) -> RedisCache:
    """
    Get the global cache instance.
    
    Args:
        config: Cache configuration (uses defaults if None)
        
    Returns:
        RedisCache instance
    """
    global _cache
    if _cache is None:
        _cache = RedisCache(config=config)
    return _cache


def get_solution_cache(config: CacheConfig = None) -> SolutionCache:
    """
    Get the global solution cache instance.
    
    Args:
        config: Cache configuration (uses defaults if None)
        
    Returns:
        SolutionCache instance
    """
    global _solution_cache
    if _solution_cache is None:
        cache = get_cache(config)
        _solution_cache = SolutionCache(cache=cache)
    return _solution_cache


def clear_cache():
    """Clear the global cache."""
    global _cache
    if _cache is not None:
        _cache.clear_all()
