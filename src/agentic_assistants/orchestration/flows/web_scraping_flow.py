"""
Prefect flow for web scraping tasks with retries and caching.
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
    @task(retries=5, retry_delay_seconds=30)
    async def scrape_url(
        url: str,
        cache_dir: Path,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Scrape a single URL with retry logic."""
        from agentic_assistants.ingestion.remote_fetcher import URLFetcher
        
        fetcher = URLFetcher(cache_dir=cache_dir, use_cache=use_cache)
        files = await fetcher.fetch(url)
        
        return {
            "url": url,
            "files": [str(f) for f in files],
            "success": len(files) > 0,
        }
    
    @task(retries=3)
    async def crawl_website(
        start_url: str,
        max_pages: int,
        cache_dir: Path,
    ) -> List[str]:
        """Crawl a website starting from start_url."""
        from agentic_assistants.ingestion.remote_fetcher import WebCrawler
        
        crawler = WebCrawler(cache_dir=cache_dir)
        files = await crawler.fetch(
            start_url=start_url,
            max_pages=max_pages,
            max_depth=3,
        )
        
        return [str(f) for f in files]
    
    @task
    def extract_content(file_paths: List[str]) -> List[Dict[str, Any]]:
        """Extract structured content from scraped files."""
        extracted = []
        
        for file_path in file_paths:
            # Placeholder for content extraction
            extracted.append({
                "file": file_path,
                "content": "extracted content",
                "metadata": {},
            })
        
        return extracted
    
    @task
    def store_content(
        extracted_data: List[Dict[str, Any]],
        output_dir: Path,
    ) -> Dict[str, int]:
        """Store extracted content."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stored_count = 0
        for item in extracted_data:
            # Store to database or file
            stored_count += 1
        
        return {
            "stored_count": stored_count,
            "output_dir": str(output_dir),
        }
    
    @flow(
        name="web-scraping",
        description="Scrape and process web content",
        task_runner=ConcurrentTaskRunner(),
    )
    async def web_scraping_flow(
        urls: Optional[List[str]] = None,
        start_url: Optional[str] = None,
        max_pages: int = 50,
        cache_dir: Path = Path("./data/fetch_cache"),
        output_dir: Path = Path("./data/scraped"),
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Web scraping workflow with concurrent URL processing.
        
        Args:
            urls: List of URLs to scrape (for specific URLs)
            start_url: Starting URL for crawling (for site crawling)
            max_pages: Maximum pages to crawl
            cache_dir: Cache directory
            output_dir: Output directory
            use_cache: Whether to use cached content
            
        Returns:
            Dict with scraping results
        """
        if urls:
            # Scrape specific URLs concurrently
            scrape_tasks = [
                scrape_url(url, cache_dir, use_cache)
                for url in urls
            ]
            results = await scrape_tasks
            
            all_files = []
            for result in results:
                if result["success"]:
                    all_files.extend(result["files"])
        
        elif start_url:
            # Crawl website
            all_files = await crawl_website(start_url, max_pages, cache_dir)
        
        else:
            raise ValueError("Either urls or start_url must be provided")
        
        # Extract content
        extracted = extract_content(all_files)
        
        # Store results
        store_result = store_content(extracted, output_dir)
        
        return {
            "files_scraped": len(all_files),
            "content_extracted": len(extracted),
            **store_result,
        }

else:
    async def web_scraping_flow(*args, **kwargs):
        raise ImportError("Prefect is required for web scraping flow")
