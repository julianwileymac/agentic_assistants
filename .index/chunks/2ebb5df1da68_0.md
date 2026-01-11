# Chunk: 2ebb5df1da68_0

- source: `src/agentic_assistants/data/telemetry.py`
- lines: 1-83
- chunk: 1/4

```
"""
Telemetry integration for data components.

Provides logging, tracing, and metrics for all data operations.
"""

import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Metrics
# ============================================================================

class DataMetrics:
    """Metrics collector for data operations."""
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._histograms: Dict[str, list] = {}
        self._gauges: Dict[str, float] = {}
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, tags)
        self._counters[key] = self._counters.get(key, 0) + value
    
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a value to a histogram."""
        key = self._make_key(name, tags)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, tags)
        self._gauges[key] = value
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a metric."""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name}|{tag_str}"
        return name
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get a counter value."""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])
        
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / n,
            "p50": sorted_values[int(n * 0.5)],
            "p95": sorted_values[int(n * 0.95)] if n >= 20 else sorted_values[-1],
            "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1],
        }
    
    def export(self) -> Dict[str, Any]:
        """Export all metrics."""
        return {
            "counters": dict(self._counters),
```
