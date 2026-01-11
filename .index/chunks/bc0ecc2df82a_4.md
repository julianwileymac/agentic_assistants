# Chunk: bc0ecc2df82a_4

- source: `src/agentic_assistants/data/layer.py`
- lines: 317-374
- chunk: 5/5

```
""
        Delete a file.
        
        Args:
            path: Path to the file to delete
            invalidate_cache: Whether to invalidate cache
        
        Returns:
            True if file was deleted, False if it didn't exist
        """
        path = Path(path)
        
        if invalidate_cache and self.cache is not None:
            cache_key = self._cache_key(path)
            self.cache.delete(cache_key)
        
        if path.exists():
            path.unlink()
            return True
        return False

    def clear_cache(self) -> None:
        """Clear the entire cache."""
        if self.cache is not None:
            self.cache.clear()
            logger.info("Data layer cache cleared")

    def get_cache_stats(self) -> Optional[dict]:
        """Get cache statistics."""
        if self.cache is not None:
            return self.cache.get_stats()
        return None

    def to_pandas(self, table: pa.Table):
        """
        Convert a PyArrow table to a pandas DataFrame.
        
        Args:
            table: PyArrow table
        
        Returns:
            pandas DataFrame
        """
        return table.to_pandas()

    def from_pandas(self, df) -> pa.Table:
        """
        Convert a pandas DataFrame to a PyArrow table.
        
        Args:
            df: pandas DataFrame
        
        Returns:
            PyArrow Table
        """
        return pa.Table.from_pandas(df)

```
