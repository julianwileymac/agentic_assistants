# Chunk: bc0ecc2df82a_1

- source: `src/agentic_assistants/data/layer.py`
- lines: 91-179
- chunk: 2/5

```
if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return self.SUPPORTED_FORMATS[ext]

    def _get_mtime(self, path: Union[str, Path]) -> Optional[float]:
        """Get file modification time."""
        path = Path(path)
        if path.exists():
            return path.stat().st_mtime
        return None

    def _cache_key(self, path: Union[str, Path]) -> str:
        """Generate a cache key for a file path."""
        return str(Path(path).resolve())

    def read(
        self,
        path: Union[str, Path],
        format: Optional[str] = None,
        use_cache: bool = True,
        **kwargs,
    ) -> Any:
        """
        Read data from a file with optional caching.
        
        Args:
            path: Path to the file to read
            format: Override format detection (parquet, json, csv, text)
            use_cache: Whether to use caching for this read
            **kwargs: Additional arguments passed to the format reader
        
        Returns:
            Data from the file (type depends on format)
        """
        path = Path(path)
        cache_key = self._cache_key(path)
        current_mtime = self._get_mtime(path)
        
        # Try cache first
        if use_cache and self.cache is not None:
            cached = self.cache.get(cache_key, current_mtime=current_mtime)
            if cached is not None:
                logger.debug(f"Cache hit: {path}")
                return cached
        
        # Determine format
        file_format = format or self._get_format(path)
        
        # Read based on format
        logger.debug(f"Reading {file_format} file: {path}")
        
        if file_format == "parquet":
            data = self._read_parquet(path, **kwargs)
        elif file_format == "json":
            data = self._read_json(path, **kwargs)
        elif file_format == "jsonl":
            data = self._read_jsonl(path, **kwargs)
        elif file_format == "csv":
            data = self._read_csv(path, **kwargs)
        elif file_format == "text":
            data = self._read_text(path, **kwargs)
        elif file_format == "yaml":
            data = self._read_yaml(path, **kwargs)
        else:
            raise ValueError(f"Unknown format: {file_format}")
        
        # Cache the result
        if use_cache and self.cache is not None:
            self.cache.set(cache_key, data, file_mtime=current_mtime)
        
        return data

    def write(
        self,
        data: Any,
        path: Union[str, Path],
        format: Optional[str] = None,
        invalidate_cache: bool = True,
        **kwargs,
    ) -> Path:
        """
        Write data to a file.
        
        Args:
            data: Data to write
            path: Path to write to
            format: Override format detection
```
