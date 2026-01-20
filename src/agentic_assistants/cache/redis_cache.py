"""
Redis-based cache implementation.

This module provides a Redis cache client with support for
various data types, TTL management, and namespace isolation.

Example:
    >>> from agentic_assistants.cache import RedisCache
    >>> 
    >>> cache = RedisCache()
    >>> 
    >>> # Basic operations
    >>> cache.set("user:123:prefs", {"theme": "dark"}, ttl=3600)
    >>> prefs = cache.get("user:123:prefs")
    >>> 
    >>> # With namespacing
    >>> cache.set("config", {"model": "llama3"}, namespace="project:abc")
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class CacheConfig(BaseModel):
    """Configuration for the Redis cache."""
    
    enabled: bool = Field(
        default=True,
        description="Enable Redis cache",
    )
    url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL",
    )
    db: int = Field(
        default=0,
        description="Redis database number",
    )
    prefix: str = Field(
        default="agentic:",
        description="Key prefix for all cache keys",
    )
    default_ttl: int = Field(
        default=3600,
        description="Default TTL in seconds",
    )
    max_connections: int = Field(
        default=10,
        description="Maximum connections in pool",
    )
    socket_timeout: float = Field(
        default=5.0,
        description="Socket timeout in seconds",
    )
    retry_on_timeout: bool = Field(
        default=True,
        description="Retry on timeout",
    )
    
    # Serialization
    serializer: str = Field(
        default="json",
        description="Serialization format (json, pickle)",
    )
    
    @classmethod
    def from_app_config(cls) -> "CacheConfig":
        """Create config from application config."""
        from agentic_assistants.config import AgenticConfig
        
        config = AgenticConfig()
        return cls(
            enabled=config.redis.enabled,
            url=config.redis.connection_url,
            db=config.redis.db,
            prefix=config.redis.prefix,
            default_ttl=config.redis.default_ttl,
            max_connections=config.redis.max_connections,
            socket_timeout=config.redis.socket_timeout,
        )


@dataclass
class CacheEntry:
    """A cached entry with metadata."""
    
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    namespace: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "namespace": self.namespace,
            "metadata": self.metadata,
        }


@dataclass
class CacheStats:
    """Cache statistics."""
    
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "hit_rate": self.hit_rate,
        }


class RedisCache:
    """
    Redis-based cache with namespace support.
    
    Provides a high-level interface for caching with Redis,
    supporting namespacing, TTL management, and various data types.
    
    Attributes:
        config: Cache configuration
        stats: Cache statistics
    
    Example:
        >>> cache = RedisCache()
        >>> 
        >>> # Simple operations
        >>> cache.set("key", "value")
        >>> value = cache.get("key")
        >>> 
        >>> # With TTL
        >>> cache.set("session", data, ttl=3600)
        >>> 
        >>> # With namespace
        >>> cache.set("config", data, namespace="project:123")
        >>> 
        >>> # Check existence
        >>> if cache.exists("key"):
        ...     cache.delete("key")
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize Redis cache.
        
        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig.from_app_config()
        self.stats = CacheStats()
        self._client = None
        self._initialized = False
    
    @property
    def client(self):
        """Get or initialize Redis client."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def _initialize_client(self):
        """Initialize the Redis client."""
        if not self.config.enabled:
            logger.info("Redis cache disabled, using in-memory fallback")
            self._client = InMemoryCache()
            self._initialized = True
            return
        
        try:
            import redis
            
            self._client = redis.from_url(
                self.config.url,
                db=self.config.db,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                max_connections=self.config.max_connections,
                decode_responses=True,
            )
            
            # Test connection
            self._client.ping()
            self._initialized = True
            logger.info(f"Connected to Redis at {self.config.url}")
            
        except ImportError:
            logger.warning("redis package not installed, using in-memory fallback")
            self._client = InMemoryCache()
            self._initialized = True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, using in-memory fallback")
            self._client = InMemoryCache()
            self._initialized = True
    
    def _make_key(self, key: str, namespace: str = "") -> str:
        """Create a full cache key with prefix and namespace."""
        parts = [self.config.prefix]
        if namespace:
            parts.append(namespace)
        parts.append(key)
        return ":".join(parts)
    
    def _serialize(self, value: Any) -> str:
        """Serialize a value for storage."""
        if self.config.serializer == "json":
            return json.dumps(value, default=str)
        else:
            import pickle
            import base64
            return base64.b64encode(pickle.dumps(value)).decode()
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize a value from storage."""
        if not data:
            return None
        
        if self.config.serializer == "json":
            return json.loads(data)
        else:
            import pickle
            import base64
            return pickle.loads(base64.b64decode(data.encode()))
    
    def get(
        self,
        key: str,
        default: Any = None,
        namespace: str = "",
    ) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            namespace: Optional namespace
            
        Returns:
            Cached value or default
        """
        full_key = self._make_key(key, namespace)
        
        try:
            data = self.client.get(full_key)
            
            if data is None:
                self.stats.misses += 1
                return default
            
            self.stats.hits += 1
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            self.stats.errors += 1
            return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "",
    ) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        full_key = self._make_key(key, namespace)
        ttl = ttl if ttl is not None else self.config.default_ttl
        
        try:
            data = self._serialize(value)
            
            if ttl > 0:
                self.client.setex(full_key, ttl, data)
            else:
                self.client.set(full_key, data)
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            self.stats.errors += 1
            return False
    
    def delete(self, key: str, namespace: str = "") -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace
            
        Returns:
            True if deleted
        """
        full_key = self._make_key(key, namespace)
        
        try:
            result = self.client.delete(full_key)
            self.stats.deletes += 1
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            self.stats.errors += 1
            return False
    
    def exists(self, key: str, namespace: str = "") -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace
            
        Returns:
            True if exists
        """
        full_key = self._make_key(key, namespace)
        
        try:
            return bool(self.client.exists(full_key))
        except Exception as e:
            logger.error(f"Cache exists error for {key}: {e}")
            return False
    
    def get_ttl(self, key: str, namespace: str = "") -> int:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            namespace: Optional namespace
            
        Returns:
            TTL in seconds (-1 if no expiry, -2 if not exists)
        """
        full_key = self._make_key(key, namespace)
        
        try:
            return self.client.ttl(full_key)
        except Exception as e:
            logger.error(f"Cache ttl error for {key}: {e}")
            return -2
    
    def set_ttl(self, key: str, ttl: int, namespace: str = "") -> bool:
        """
        Set TTL for an existing key.
        
        Args:
            key: Cache key
            ttl: New TTL in seconds
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        full_key = self._make_key(key, namespace)
        
        try:
            return bool(self.client.expire(full_key, ttl))
        except Exception as e:
            logger.error(f"Cache set_ttl error for {key}: {e}")
            return False
    
    def get_many(
        self,
        keys: List[str],
        namespace: str = "",
    ) -> Dict[str, Any]:
        """
        Get multiple values from the cache.
        
        Args:
            keys: List of cache keys
            namespace: Optional namespace
            
        Returns:
            Dictionary of key -> value
        """
        full_keys = [self._make_key(k, namespace) for k in keys]
        
        try:
            values = self.client.mget(full_keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
                    self.stats.hits += 1
                else:
                    self.stats.misses += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            self.stats.errors += 1
            return {}
    
    def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None,
        namespace: str = "",
    ) -> bool:
        """
        Set multiple values in the cache.
        
        Args:
            items: Dictionary of key -> value
            ttl: Time-to-live in seconds
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        ttl = ttl if ttl is not None else self.config.default_ttl
        
        try:
            pipe = self.client.pipeline()
            
            for key, value in items.items():
                full_key = self._make_key(key, namespace)
                data = self._serialize(value)
                
                if ttl > 0:
                    pipe.setex(full_key, ttl, data)
                else:
                    pipe.set(full_key, data)
            
            pipe.execute()
            self.stats.sets += len(items)
            return True
            
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            self.stats.errors += 1
            return False
    
    def delete_many(self, keys: List[str], namespace: str = "") -> int:
        """
        Delete multiple keys from the cache.
        
        Args:
            keys: List of cache keys
            namespace: Optional namespace
            
        Returns:
            Number of keys deleted
        """
        full_keys = [self._make_key(k, namespace) for k in keys]
        
        try:
            count = self.client.delete(*full_keys)
            self.stats.deletes += count
            return count
        except Exception as e:
            logger.error(f"Cache delete_many error: {e}")
            self.stats.errors += 1
            return 0
    
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            Number of keys deleted
        """
        pattern = self._make_key("*", namespace)
        
        try:
            keys = list(self.client.scan_iter(match=pattern))
            if keys:
                count = self.client.delete(*keys)
                self.stats.deletes += count
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache clear_namespace error: {e}")
            self.stats.errors += 1
            return 0
    
    def clear_all(self) -> int:
        """
        Clear all keys with our prefix.
        
        Returns:
            Number of keys deleted
        """
        pattern = f"{self.config.prefix}*"
        
        try:
            keys = list(self.client.scan_iter(match=pattern))
            if keys:
                count = self.client.delete(*keys)
                self.stats.deletes += count
                logger.info(f"Cleared {count} cache keys")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache clear_all error: {e}")
            self.stats.errors += 1
            return 0
    
    def get_keys(self, pattern: str = "*", namespace: str = "") -> List[str]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern: Key pattern (supports *)
            namespace: Optional namespace
            
        Returns:
            List of matching keys (without prefix/namespace)
        """
        full_pattern = self._make_key(pattern, namespace)
        prefix_len = len(self._make_key("", namespace))
        
        try:
            keys = list(self.client.scan_iter(match=full_pattern))
            return [k[prefix_len:] for k in keys]
        except Exception as e:
            logger.error(f"Cache get_keys error: {e}")
            return []
    
    def increment(
        self,
        key: str,
        amount: int = 1,
        namespace: str = "",
    ) -> int:
        """
        Increment a counter.
        
        Args:
            key: Cache key
            amount: Amount to increment
            namespace: Optional namespace
            
        Returns:
            New value
        """
        full_key = self._make_key(key, namespace)
        
        try:
            return self.client.incrby(full_key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for {key}: {e}")
            self.stats.errors += 1
            return 0
    
    def decrement(
        self,
        key: str,
        amount: int = 1,
        namespace: str = "",
    ) -> int:
        """
        Decrement a counter.
        
        Args:
            key: Cache key
            amount: Amount to decrement
            namespace: Optional namespace
            
        Returns:
            New value
        """
        full_key = self._make_key(key, namespace)
        
        try:
            return self.client.decrby(full_key, amount)
        except Exception as e:
            logger.error(f"Cache decrement error for {key}: {e}")
            self.stats.errors += 1
            return 0
    
    def get_info(self) -> Dict[str, Any]:
        """Get cache information and stats."""
        info = {
            "enabled": self.config.enabled,
            "url": self.config.url,
            "prefix": self.config.prefix,
            "initialized": self._initialized,
            "stats": self.stats.to_dict(),
        }
        
        try:
            if self._initialized and hasattr(self.client, 'info'):
                redis_info = self.client.info()
                info["redis"] = {
                    "version": redis_info.get("redis_version"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "used_memory_human": redis_info.get("used_memory_human"),
                    "total_keys": sum(
                        v for k, v in redis_info.items()
                        if k.startswith("db") and isinstance(v, dict)
                        and "keys" in v
                    ),
                }
        except Exception:
            pass
        
        return info


class InMemoryCache:
    """
    In-memory cache fallback when Redis is unavailable.
    
    Provides a simple dictionary-based cache with TTL support.
    """
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get a value."""
        entry = self._data.get(key)
        if entry is None:
            return None
        
        # Check TTL
        if entry.get("expires_at"):
            if time.time() > entry["expires_at"]:
                del self._data[key]
                return None
        
        return entry.get("value")
    
    def set(self, key: str, value: str) -> bool:
        """Set a value without TTL."""
        self._data[key] = {"value": value}
        return True
    
    def setex(self, key: str, ttl: int, value: str) -> bool:
        """Set a value with TTL."""
        self._data[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
        }
        return True
    
    def delete(self, *keys: str) -> int:
        """Delete keys."""
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None
    
    def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        entry = self._data.get(key)
        if entry is None:
            return -2
        if "expires_at" not in entry:
            return -1
        remaining = entry["expires_at"] - time.time()
        return max(0, int(remaining))
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key."""
        if key in self._data:
            self._data[key]["expires_at"] = time.time() + ttl
            return True
        return False
    
    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """Get multiple values."""
        return [self.get(k) for k in keys]
    
    def pipeline(self) -> "InMemoryPipeline":
        """Get a pipeline."""
        return InMemoryPipeline(self)
    
    def scan_iter(self, match: str = "*") -> List[str]:
        """Scan keys matching pattern."""
        import fnmatch
        pattern = match.replace(":", "")
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, match)]
    
    def incrby(self, key: str, amount: int) -> int:
        """Increment a counter."""
        current = self.get(key)
        if current is None:
            new_value = amount
        else:
            new_value = int(current) + amount
        self.set(key, str(new_value))
        return new_value
    
    def decrby(self, key: str, amount: int) -> int:
        """Decrement a counter."""
        return self.incrby(key, -amount)
    
    def ping(self) -> bool:
        """Ping (always succeeds for in-memory)."""
        return True


class InMemoryPipeline:
    """Pipeline for in-memory cache."""
    
    def __init__(self, cache: InMemoryCache):
        self._cache = cache
        self._commands: List[tuple] = []
    
    def set(self, key: str, value: str):
        self._commands.append(("set", key, value))
        return self
    
    def setex(self, key: str, ttl: int, value: str):
        self._commands.append(("setex", key, ttl, value))
        return self
    
    def execute(self):
        results = []
        for cmd in self._commands:
            if cmd[0] == "set":
                results.append(self._cache.set(cmd[1], cmd[2]))
            elif cmd[0] == "setex":
                results.append(self._cache.setex(cmd[1], cmd[2], cmd[3]))
        self._commands = []
        return results
