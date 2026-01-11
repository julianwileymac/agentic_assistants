"""
Pre-built job types for common data operations.
"""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class JobResult:
    """Result of a job execution."""
    
    success: bool
    job_id: str
    executed_at: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    items_processed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "job_id": self.job_id,
            "executed_at": self.executed_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "items_processed": self.items_processed,
            "errors": self.errors,
            "metadata": self.metadata,
        }


class Job(ABC):
    """Abstract base class for scheduled jobs."""
    
    def __init__(
        self,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self._job_id = job_id
        self._name = name
        self._last_result: Optional[JobResult] = None
    
    @property
    def job_id(self) -> str:
        if self._job_id is None:
            self._job_id = f"{self.__class__.__name__}_{id(self)}"
        return self._job_id
    
    @property
    def name(self) -> str:
        return self._name or self.__class__.__name__
    
    @abstractmethod
    def execute(self) -> JobResult:
        """Execute the job."""
        pass
    
    def run(self) -> None:
        """Run the job (called by scheduler)."""
        import time
        
        start_time = time.time()
        logger.info(f"Starting job: {self.name}")
        
        try:
            result = self.execute()
            result.duration_seconds = time.time() - start_time
            self._last_result = result
            
            if result.success:
                logger.info(
                    f"Job {self.name} completed: "
                    f"{result.items_processed} items in {result.duration_seconds:.2f}s"
                )
            else:
                logger.error(f"Job {self.name} failed: {result.errors}")
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Job {self.name} raised exception: {e}")
            self._last_result = JobResult(
                success=False,
                job_id=self.job_id,
                duration_seconds=duration,
                errors=[str(e)],
            )
    
    @property
    def last_result(self) -> Optional[JobResult]:
        return self._last_result


class RSSMonitorJob(Job):
    """Job for monitoring RSS feeds."""
    
    def __init__(
        self,
        feed_url: str,
        collection: str = "rss_content",
        max_entries: int = 20,
        job_id: Optional[str] = None,
    ):
        super().__init__(job_id, f"RSS Monitor: {feed_url[:50]}")
        self.feed_url = feed_url
        self.collection = collection
        self.max_entries = max_entries
        self._seen_ids: set = set()
    
    def execute(self) -> JobResult:
        from agentic_assistants.data.rag import IngestionPipeline, IngestionConfig
        from agentic_assistants.data.datasets import RSSDataset
        
        try:
            # Fetch RSS feed
            dataset = RSSDataset(url=self.feed_url, max_entries=self.max_entries)
            feed_data = dataset.load()
            
            entries = feed_data.get("entries", [])
            new_entries = []
            
            # Filter to new entries
            for entry in entries:
                entry_id = entry.get("id") or entry.get("link") or entry.get("title")
                if entry_id and entry_id not in self._seen_ids:
                    new_entries.append(entry)
                    self._seen_ids.add(entry_id)
            
            if not new_entries:
                return JobResult(
                    success=True,
                    job_id=self.job_id,
                    items_processed=0,
                    metadata={"message": "No new entries"},
                )
            
            # Ingest new entries
            pipeline = IngestionPipeline(
                config=IngestionConfig(collection=self.collection)
            )
            
            total_stored = 0
            for entry in new_entries:
                content = f"{entry.get('title', '')}\n\n{entry.get('content', entry.get('summary', ''))}"
                result = pipeline.ingest(
                    source=content,
                    source_type="text",
                    collection=self.collection,
                    metadata={
                        "url": entry.get("link"),
                        "published": entry.get("published"),
                        "feed_url": self.feed_url,
                    },
                )
                total_stored += result.chunks_stored
            
            return JobResult(
                success=True,
                job_id=self.job_id,
                items_processed=len(new_entries),
                metadata={
                    "chunks_stored": total_stored,
                    "feed_url": self.feed_url,
                },
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=self.job_id,
                errors=[str(e)],
            )


class WebsiteMonitorJob(Job):
    """Job for monitoring website changes."""
    
    def __init__(
        self,
        url: str,
        selectors: Dict[str, str],
        collection: str = "web_content",
        job_id: Optional[str] = None,
    ):
        super().__init__(job_id, f"Website Monitor: {url[:50]}")
        self.url = url
        self.selectors = selectors
        self.collection = collection
        self._last_content_hash: Optional[str] = None
    
    def execute(self) -> JobResult:
        from agentic_assistants.data.datasets import WebsiteDataset
        from agentic_assistants.data.rag import IngestionPipeline
        
        try:
            # Scrape website
            dataset = WebsiteDataset(url=self.url, selectors=self.selectors)
            content = dataset.load()
            
            # Compute content hash
            content_str = str(content)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Check if content changed
            if content_hash == self._last_content_hash:
                return JobResult(
                    success=True,
                    job_id=self.job_id,
                    items_processed=0,
                    metadata={"message": "No changes detected"},
                )
            
            self._last_content_hash = content_hash
            
            # Ingest changed content
            pipeline = IngestionPipeline()
            result = pipeline.ingest(
                source=content_str,
                source_type="text",
                collection=self.collection,
                metadata={"url": self.url, "scraped_at": datetime.utcnow().isoformat()},
            )
            
            return JobResult(
                success=True,
                job_id=self.job_id,
                items_processed=1,
                metadata={
                    "chunks_stored": result.chunks_stored,
                    "url": self.url,
                },
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=self.job_id,
                errors=[str(e)],
            )


class DataSyncJob(Job):
    """Job for syncing data from sources."""
    
    def __init__(
        self,
        source_id: str,
        collection: str,
        job_id: Optional[str] = None,
    ):
        super().__init__(job_id, f"Data Sync: {source_id}")
        self.source_id = source_id
        self.collection = collection
    
    def execute(self) -> JobResult:
        from agentic_assistants.data.catalog import DataCatalog
        from agentic_assistants.data.rag import IngestionPipeline
        
        try:
            catalog = DataCatalog()
            
            # Load data from source
            data = catalog.load(self.source_id)
            
            if data is None:
                return JobResult(
                    success=False,
                    job_id=self.job_id,
                    errors=[f"Source not found: {self.source_id}"],
                )
            
            # Convert to text if needed
            if isinstance(data, str):
                content = data
            elif hasattr(data, "to_string"):
                content = data.to_string()
            else:
                content = str(data)
            
            # Ingest
            pipeline = IngestionPipeline()
            result = pipeline.ingest(
                source=content,
                source_type="text",
                collection=self.collection,
                metadata={"source_id": self.source_id},
            )
            
            return JobResult(
                success=True,
                job_id=self.job_id,
                items_processed=1,
                metadata={"chunks_stored": result.chunks_stored},
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=self.job_id,
                errors=[str(e)],
            )


class FeatureMaterializationJob(Job):
    """Job for materializing features to online store."""
    
    def __init__(
        self,
        feature_views: Optional[List[str]] = None,
        days: int = 7,
        job_id: Optional[str] = None,
    ):
        super().__init__(job_id, "Feature Materialization")
        self.feature_views = feature_views
        self.days = days
    
    def execute(self) -> JobResult:
        from datetime import timedelta
        from agentic_assistants.features import get_feature_store
        
        try:
            store = get_feature_store()
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.days)
            
            results = store.materialize(
                feature_views=self.feature_views,
                start_date=start_date,
                end_date=end_date,
            )
            
            total_rows = sum(results.values())
            
            return JobResult(
                success=True,
                job_id=self.job_id,
                items_processed=total_rows,
                metadata={
                    "views_materialized": results,
                    "date_range": f"{start_date.date()} to {end_date.date()}",
                },
            )
            
        except Exception as e:
            return JobResult(
                success=False,
                job_id=self.job_id,
                errors=[str(e)],
            )
