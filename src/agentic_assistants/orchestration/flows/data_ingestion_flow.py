"""
Prefect flow for data ingestion pipelines.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from prefect import flow, task
    from prefect.task_runners import ConcurrentTaskRunner
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


if PREFECT_AVAILABLE:
    @task(retries=3, retry_delay_seconds=10)
    async def fetch_remote_data(source_url: str, cache_dir: Path) -> Path:
        """Fetch data from remote source."""
        from agentic_assistants.ingestion.remote_fetcher import URLFetcher
        
        fetcher = URLFetcher(cache_dir=cache_dir)
        files = await fetcher.fetch(source_url)
        
        return files[0] if files else None
    
    @task
    def validate_data(file_path: Path) -> bool:
        """Validate downloaded data."""
        if not file_path or not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        # Add validation logic
        return True
    
    @task
    def transform_data(file_path: Path, output_dir: Path) -> Path:
        """Transform raw data to processed format."""
        import shutil
        
        output_path = output_dir / file_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(file_path, output_path)
        logger.info(f"Transformed data saved to: {output_path}")
        
        return output_path
    
    @task
    def index_data(file_path: Path, collection_name: str) -> Dict[str, Any]:
        """Index processed data for search."""
        # Placeholder for indexing logic
        return {
            "file_path": str(file_path),
            "collection": collection_name,
            "indexed": True,
        }
    
    @flow(
        name="data-ingestion",
        description="Fetch, validate, transform, and index data",
        task_runner=ConcurrentTaskRunner(),
    )
    async def data_ingestion_flow(
        source_url: str,
        cache_dir: Path = Path("./data/fetch_cache"),
        output_dir: Path = Path("./data/processed"),
        collection_name: str = "default",
    ) -> Dict[str, Any]:
        """
        Complete data ingestion workflow.
        
        Args:
            source_url: URL of data source
            cache_dir: Directory for caching downloads
            output_dir: Directory for processed data
            collection_name: Name of vector store collection
            
        Returns:
            Dict with ingestion results
        """
        # Fetch data
        raw_file = await fetch_remote_data(source_url, cache_dir)
        
        # Validate
        is_valid = validate_data(raw_file)
        
        if not is_valid:
            raise ValueError("Data validation failed")
        
        # Transform
        processed_file = transform_data(raw_file, output_dir)
        
        # Index
        index_result = index_data(processed_file, collection_name)
        
        return {
            "source_url": source_url,
            "raw_file": str(raw_file),
            "processed_file": str(processed_file),
            "index_result": index_result,
        }

else:
    async def data_ingestion_flow(*args, **kwargs):
        raise ImportError("Prefect is required for data ingestion flow")
