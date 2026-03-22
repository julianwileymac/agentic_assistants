"""
Template for web scraping jobs.

Usage:
    python web_scraper.py --url https://example.com --output ./data/scraped
"""

import argparse
import asyncio
from pathlib import Path


async def scrape_website(url: str, output_dir: Path):
    """Scrape a website and save content."""
    from agentic_assistants.ingestion.remote_fetcher import WebCrawler
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    crawler = WebCrawler(cache_dir=output_dir)
    files = await crawler.fetch(
        start_url=url,
        max_pages=50,
        max_depth=3,
    )
    
    print(f"Scraped {len(files)} pages from {url}")
    return files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Web scraping template")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--output", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    asyncio.run(scrape_website(args.url, Path(args.output)))


if __name__ == "__main__":
    main()
