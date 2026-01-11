# Chunk: bc0ecc2df82a_2

- source: `src/agentic_assistants/data/layer.py`
- lines: 167-254
- chunk: 3/5

```

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
            invalidate_cache: Whether to invalidate cache for this path
            **kwargs: Additional arguments passed to the format writer
        
        Returns:
            Path to the written file
        """
        path = Path(path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format
        file_format = format or self._get_format(path)
        
        # Write based on format
        logger.debug(f"Writing {file_format} file: {path}")
        
        if file_format == "parquet":
            self._write_parquet(data, path, **kwargs)
        elif file_format == "json":
            self._write_json(data, path, **kwargs)
        elif file_format == "jsonl":
            self._write_jsonl(data, path, **kwargs)
        elif file_format == "csv":
            self._write_csv(data, path, **kwargs)
        elif file_format == "text":
            self._write_text(data, path, **kwargs)
        elif file_format == "yaml":
            self._write_yaml(data, path, **kwargs)
        else:
            raise ValueError(f"Unknown format: {file_format}")
        
        # Invalidate cache
        if invalidate_cache and self.cache is not None:
            cache_key = self._cache_key(path)
            self.cache.delete(cache_key)
        
        return path

    # === Format-specific readers ===

    def _read_parquet(self, path: Path, **kwargs) -> pa.Table:
        """Read a Parquet file."""
        return pq.read_table(path, **kwargs)

    def _read_json(self, path: Path, **kwargs) -> Any:
        """Read a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f, **kwargs)

    def _read_jsonl(self, path: Path, **kwargs) -> list:
        """Read a JSON Lines file."""
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _read_csv(self, path: Path, **kwargs) -> pa.Table:
        """Read a CSV file as a PyArrow table."""
        import pyarrow.csv as pv
        return pv.read_csv(path, **kwargs)

    def _read_text(self, path: Path, encoding: str = "utf-8", **kwargs) -> str:
        """Read a text file."""
        return path.read_text(encoding=encoding)

    def _read_yaml(self, path: Path, **kwargs) -> Any:
        """Read a YAML file."""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

```
