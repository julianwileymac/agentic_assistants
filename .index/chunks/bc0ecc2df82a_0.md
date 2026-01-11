# Chunk: bc0ecc2df82a_0

- source: `src/agentic_assistants/data/layer.py`
- lines: 1-99
- chunk: 1/5

```
"""
Data layer for unified I/O operations with caching.

This module provides a DataLayer class that abstracts file I/O operations
with intelligent caching and format auto-detection.

Example:
    >>> from agentic_assistants.data import DataLayer
    >>> 
    >>> layer = DataLayer()
    >>> df = layer.read("data/users.parquet")  # Cached
    >>> layer.write(df, "output/results.parquet")
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Union

import pyarrow as pa
import pyarrow.parquet as pq

from agentic_assistants.config import AgenticConfig
from agentic_assistants.data.cache import LRUCache
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DataLayer:
    """
    Unified data I/O layer with caching and format support.
    
    This class provides:
    - Automatic format detection based on file extension
    - LRU caching with file modification tracking
    - Preference for Parquet format for tabular data
    - Support for common data formats (parquet, json, csv, text)
    
    Attributes:
        config: Agentic configuration instance
        cache: LRU cache for read operations
    """

    # Supported file extensions and their handlers
    SUPPORTED_FORMATS = {
        ".parquet": "parquet",
        ".pq": "parquet",
        ".json": "json",
        ".jsonl": "jsonl",
        ".csv": "csv",
        ".txt": "text",
        ".md": "text",
        ".py": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        cache_enabled: Optional[bool] = None,
    ):
        """
        Initialize the data layer.
        
        Args:
            config: Configuration instance. If None, uses default config.
            cache_enabled: Override cache setting from config
        """
        self.config = config or AgenticConfig()
        
        # Determine cache settings
        use_cache = cache_enabled if cache_enabled is not None else self.config.data_layer.cache_enabled
        
        if use_cache:
            self.cache = LRUCache(
                max_size=self.config.data_layer.cache_max_size,
                ttl_seconds=self.config.data_layer.cache_ttl_seconds,
            )
        else:
            self.cache = None
        
        logger.debug(f"DataLayer initialized (cache_enabled={use_cache})")

    def _get_format(self, path: Union[str, Path]) -> str:
        """Determine file format from extension."""
        path = Path(path)
        ext = path.suffix.lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return self.SUPPORTED_FORMATS[ext]

    def _get_mtime(self, path: Union[str, Path]) -> Optional[float]:
        """Get file modification time."""
        path = Path(path)
```
