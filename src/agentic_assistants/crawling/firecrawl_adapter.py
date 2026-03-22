"""
Firecrawl integration for advanced web scraping.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class FirecrawlAdapter:
    """
    Adapter for Firecrawl web scraping service.
    
    Features:
    - LLM-powered content extraction
    - Sitemap generation
    - Smart crawling strategies
    - Structured data extraction
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """Initialize Firecrawl adapter."""
        if not FIRECRAWL_AVAILABLE:
            raise ImportError("firecrawl-py is required. Install with: pip install firecrawl-py")
        
        import os
        
        self.config = config or AgenticConfig()
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        
        if not self.api_key:
            raise ValueError("Firecrawl API key is required")
        
        self.client = FirecrawlApp(api_key=self.api_key)
        logger.info("Firecrawl adapter initialized")
    
    def scrape_url(
        self,
        url: str,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a single URL.
        
        Args:
            url: URL to scrape
            formats: Output formats (markdown, html, text)
            
        Returns:
            Dict with scraped content
        """
        formats = formats or ["markdown"]
        
        logger.info(f"Scraping URL with Firecrawl: {url}")
        
        result = self.client.scrape_url(
            url,
            params={"formats": formats}
        )
        
        return result
    
    def crawl_website(
        self,
        url: str,
        max_pages: int = 50,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Crawl a website starting from URL.
        
        Args:
            url: Starting URL
            max_pages: Maximum pages to crawl
            exclude_patterns: URL patterns to exclude
            
        Returns:
            List of scraped pages
        """
        logger.info(f"Crawling website with Firecrawl: {url}")
        
        crawl_result = self.client.crawl_url(
            url,
            params={
                "limit": max_pages,
                "excludes": exclude_patterns or [],
            }
        )
        
        return crawl_result.get("data", [])
    
    def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract structured data using a schema.
        
        Args:
            url: URL to extract from
            schema: JSON schema for extraction
            
        Returns:
            Extracted structured data
        """
        logger.info(f"Extracting structured data from: {url}")
        
        result = self.client.extract(url, schema)
        return result
