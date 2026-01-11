# Chunk: bc0ecc2df82a_3

- source: `src/agentic_assistants/data/layer.py`
- lines: 244-329
- chunk: 4/5

```
) -> str:
        """Read a text file."""
        return path.read_text(encoding=encoding)

    def _read_yaml(self, path: Path, **kwargs) -> Any:
        """Read a YAML file."""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # === Format-specific writers ===

    def _write_parquet(
        self,
        data: Union[pa.Table, dict, list],
        path: Path,
        **kwargs,
    ) -> None:
        """Write data to a Parquet file."""
        if isinstance(data, pa.Table):
            table = data
        elif isinstance(data, dict):
            table = pa.Table.from_pydict(data)
        elif isinstance(data, list):
            table = pa.Table.from_pylist(data)
        else:
            raise TypeError(f"Cannot convert {type(data)} to Parquet table")
        
        pq.write_table(table, path, **kwargs)

    def _write_json(self, data: Any, path: Path, indent: int = 2, **kwargs) -> None:
        """Write data to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, **kwargs)

    def _write_jsonl(self, data: list, path: Path, **kwargs) -> None:
        """Write data to a JSON Lines file."""
        with open(path, "w", encoding="utf-8") as f:
            for record in data:
                f.write(json.dumps(record, **kwargs) + "\n")

    def _write_csv(self, data: Union[pa.Table, dict, list], path: Path, **kwargs) -> None:
        """Write data to a CSV file."""
        import pyarrow.csv as pv
        
        if isinstance(data, pa.Table):
            table = data
        elif isinstance(data, dict):
            table = pa.Table.from_pydict(data)
        elif isinstance(data, list):
            table = pa.Table.from_pylist(data)
        else:
            raise TypeError(f"Cannot convert {type(data)} to CSV")
        
        pv.write_csv(table, path, **kwargs)

    def _write_text(self, data: str, path: Path, encoding: str = "utf-8", **kwargs) -> None:
        """Write data to a text file."""
        path.write_text(data, encoding=encoding)

    def _write_yaml(self, data: Any, path: Path, **kwargs) -> None:
        """Write data to a YAML file."""
        import yaml
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, **kwargs)

    # === Utility methods ===

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a file exists."""
        return Path(path).exists()

    def delete(self, path: Union[str, Path], invalidate_cache: bool = True) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file to delete
            invalidate_cache: Whether to invalidate cache
        
        Returns:
            True if file was deleted, False if it didn't exist
        """
        path = Path(path)
        
```
