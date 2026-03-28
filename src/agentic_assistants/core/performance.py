"""
Performance utilities: timing, caching, retry, rate limiting, batch processing.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from collections import OrderedDict
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def timed(fn: F) -> F:
    """Decorator that logs function execution time."""

    if asyncio.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return await fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logger.info("%s completed in %.3fs", fn.__qualname__, elapsed)

        return async_wrapper  # type: ignore[return-value]

    @functools.wraps(fn)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.info("%s completed in %.3fs", fn.__qualname__, elapsed)

    return sync_wrapper  # type: ignore[return-value]


class TTLCache:
    """Simple TTL + LRU cache."""

    def __init__(self, maxsize: int = 128, ttl_seconds: float = 300) -> None:
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any:
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self._ttl:
                self._cache.move_to_end(key)
                return val
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self._maxsize:
            self._cache.popitem(last=False)
        self._cache[key] = (time.time(), value)

    def clear(self) -> None:
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


def cached(maxsize: int = 128, ttl_seconds: float = 300) -> Callable:
    """Decorator for TTL+LRU caching of sync function results."""
    cache = TTLCache(maxsize=maxsize, ttl_seconds=ttl_seconds)

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{fn.__qualname__}:{args}:{sorted(kwargs.items())}"
            result = cache.get(key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            cache.set(key, result)
            return result

        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper

    return decorator


def async_cached(maxsize: int = 128, ttl_seconds: float = 300) -> Callable:
    """Decorator for TTL+LRU caching of async function results."""
    cache = TTLCache(maxsize=maxsize, ttl_seconds=ttl_seconds)

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{fn.__qualname__}:{args}:{sorted(kwargs.items())}"
            result = cache.get(key)
            if result is not None:
                return result
            result = await fn(*args, **kwargs)
            cache.set(key, result)
            return result

        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator for retry with exponential backoff."""

    def decorator(fn: Callable) -> Callable:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions as e:
                        last_exc = e
                        if attempt < max_attempts:
                            delay = min(
                                base_delay * (2 ** (attempt - 1)) if exponential else base_delay,
                                max_delay,
                            )
                            logger.warning(
                                "%s attempt %d/%d failed: %s (retry in %.1fs)",
                                fn.__qualname__, attempt, max_attempts, e, delay,
                            )
                            await asyncio.sleep(delay)
                raise last_exc  # type: ignore[misc]

            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        return fn(*args, **kwargs)
                    except exceptions as e:
                        last_exc = e
                        if attempt < max_attempts:
                            delay = min(
                                base_delay * (2 ** (attempt - 1)) if exponential else base_delay,
                                max_delay,
                            )
                            logger.warning(
                                "%s attempt %d/%d failed: %s (retry in %.1fs)",
                                fn.__qualname__, attempt, max_attempts, e, delay,
                            )
                            time.sleep(delay)
                raise last_exc  # type: ignore[misc]

            return sync_wrapper

    return decorator


class BatchProcessor:
    """Process items in configurable chunk sizes with optional concurrency."""

    def __init__(self, batch_size: int = 100) -> None:
        self.batch_size = batch_size

    def process(
        self,
        items: list[Any],
        fn: Callable[[list[Any]], Any],
    ) -> list[Any]:
        results = []
        for i in range(0, len(items), self.batch_size):
            chunk = items[i : i + self.batch_size]
            result = fn(chunk)
            results.append(result)
        return results

    async def aprocess(
        self,
        items: list[Any],
        fn: Callable,
        concurrency: int = 1,
    ) -> list[Any]:
        """Process batches with bounded concurrency via semaphore."""
        sem = asyncio.Semaphore(concurrency)
        batches = [items[i : i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        async def _run(chunk: list[Any]) -> Any:
            async with sem:
                return await fn(chunk)

        if concurrency <= 1:
            results = []
            for batch in batches:
                results.append(await fn(batch))
            return results

        return list(await asyncio.gather(*[_run(b) for b in batches]))


class RateLimiter:
    """Token-bucket rate limiter for API call throttling."""

    def __init__(self, rate: float, burst: int = 1) -> None:
        self._rate = rate
        self._burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    async def acquire(self) -> None:
        """Wait until a token is available, then consume it."""
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)

    def try_acquire(self) -> bool:
        """Non-blocking acquire: return True if a token was consumed."""
        self._refill()
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False


class LazyLoader:
    """Deferred module import to speed up startup."""

    def __init__(self, module_path: str) -> None:
        self._module_path = module_path
        self._module: Any = None

    def __getattr__(self, name: str) -> Any:
        if self._module is None:
            import importlib
            self._module = importlib.import_module(self._module_path)
        return getattr(self._module, name)


__all__ = [
    "timed",
    "TTLCache",
    "cached",
    "async_cached",
    "retry",
    "BatchProcessor",
    "RateLimiter",
    "LazyLoader",
]
