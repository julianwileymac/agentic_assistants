"""
Remote data fetching for document ingestion.

This module provides fetchers for retrieving documents from remote sources:
- URL fetcher (web pages, documents)
- GitHub fetcher (repositories)
- S3/MinIO fetcher (object storage)

Example:
    >>> from agentic_assistants.ingestion.remote_fetcher import GitHubFetcher
    >>> 
    >>> fetcher = GitHubFetcher()
    >>> result = await fetcher.fetch(
    ...     repo_url="https://github.com/user/repo",
    ...     branch="main",
    ... )
"""

import asyncio
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FetchResult:
    """Result from a fetch operation."""
    
    success: bool
    source: str
    files: List[str] = field(default_factory=list)
    total_size: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "source": self.source,
            "files": self.files,
            "total_size": self.total_size,
            "errors": self.errors,
            "metadata": self.metadata,
        }


class RemoteFetcher(ABC):
    """Abstract base class for remote fetchers."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize fetcher with configuration."""
        self.config = config or AgenticConfig()
        self._cache_dir = self.config.data_dir / "fetch_cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def fetch(self, **kwargs) -> Dict[str, Any]:
        """Fetch content from remote source."""
        pass
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache path for a key."""
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)
        return self._cache_dir / safe_key


class URLFetcher(RemoteFetcher):
    """
    Fetcher for web URLs.
    
    Supports fetching web pages and downloadable documents.
    
    Example:
        >>> fetcher = URLFetcher()
        >>> result = await fetcher.fetch(url="https://example.com/doc.pdf")
    """
    
    async def fetch(
        self,
        url: str,
        filename: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            filename: Override filename for saved content
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            use_cache: Use cached version if available
            
        Returns:
            FetchResult dictionary
        """
        import httpx
        
        result = FetchResult(source=url, success=False)
        
        # Check cache
        cache_key = url.replace("/", "_").replace(":", "_")
        cache_path = self._get_cache_path(cache_key)
        
        if use_cache and cache_path.exists():
            result.success = True
            result.files = [str(cache_path)]
            result.total_size = cache_path.stat().st_size
            result.metadata["from_cache"] = True
            return result.to_dict()
        
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout,
                headers=headers or {},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.content
                
                # Determine filename
                if not filename:
                    # Try Content-Disposition header
                    cd = response.headers.get("content-disposition", "")
                    if "filename=" in cd:
                        filename = cd.split("filename=")[1].strip('"').strip("'")
                    else:
                        # Use URL path
                        parsed = urlparse(url)
                        filename = Path(parsed.path).name or "document"
                
                # Add extension based on content type if missing
                if not Path(filename).suffix:
                    content_type = response.headers.get("content-type", "")
                    ext = self._content_type_to_ext(content_type)
                    if ext:
                        filename = f"{filename}{ext}"
                
                # Save to cache
                file_path = cache_path.parent / f"{cache_key}_{filename}"
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                result.success = True
                result.files = [str(file_path)]
                result.total_size = len(content)
                result.metadata = {
                    "content_type": response.headers.get("content-type"),
                    "filename": filename,
                    "fetched_at": datetime.utcnow().isoformat(),
                }
                
                logger.info(f"Fetched URL: {url} ({len(content)} bytes)")
                
        except httpx.HTTPError as e:
            result.errors.append(f"HTTP error: {str(e)}")
            logger.error(f"HTTP error fetching {url}: {e}")
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error fetching {url}: {e}")
        
        return result.to_dict()
    
    def _content_type_to_ext(self, content_type: str) -> Optional[str]:
        """Convert content type to file extension."""
        mappings = {
            "text/html": ".html",
            "text/plain": ".txt",
            "application/pdf": ".pdf",
            "application/json": ".json",
            "text/markdown": ".md",
            "application/xml": ".xml",
            "text/xml": ".xml",
        }
        for ct, ext in mappings.items():
            if ct in content_type.lower():
                return ext
        return None


class GitHubFetcher(RemoteFetcher):
    """
    Fetcher for GitHub repositories.
    
    Supports cloning repositories and fetching specific paths.
    
    Example:
        >>> fetcher = GitHubFetcher()
        >>> result = await fetcher.fetch(
        ...     repo_url="https://github.com/user/repo",
        ...     branch="main",
        ...     paths=["src/", "README.md"],
        ... )
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        github_token: Optional[str] = None,
    ):
        """
        Initialize GitHub fetcher.
        
        Args:
            config: Application configuration
            github_token: GitHub personal access token (for private repos)
        """
        super().__init__(config)
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
    
    async def fetch(
        self,
        repo_url: str,
        branch: str = "main",
        paths: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        depth: int = 1,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch content from a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to fetch
            paths: Specific paths to include (empty = all)
            exclude_patterns: Patterns to exclude
            depth: Clone depth (1 = shallow)
            force_refresh: Force re-clone even if cached
            
        Returns:
            FetchResult dictionary
        """
        result = FetchResult(source=repo_url, success=False)
        
        # Parse repo info
        repo_name = self._parse_repo_name(repo_url)
        if not repo_name:
            result.errors.append(f"Invalid GitHub URL: {repo_url}")
            return result.to_dict()
        
        # Determine cache path
        cache_path = self._cache_dir / "github" / repo_name
        
        try:
            # Clone or update repository
            if cache_path.exists() and not force_refresh:
                # Pull latest
                await self._git_pull(cache_path, branch)
            else:
                # Clone fresh
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                await self._git_clone(repo_url, cache_path, branch, depth)
            
            # Collect files
            exclude_patterns = exclude_patterns or [
                "*.pyc", "__pycache__", "node_modules", ".git",
                "*.egg-info", "dist", "build", ".venv", "venv",
            ]
            
            files = []
            total_size = 0
            
            for file_path in cache_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Check if in specified paths
                if paths:
                    relative = file_path.relative_to(cache_path)
                    in_paths = any(
                        str(relative).startswith(p.rstrip("/"))
                        for p in paths
                    )
                    if not in_paths:
                        continue
                
                # Check exclusions
                skip = False
                for pattern in exclude_patterns:
                    if file_path.match(pattern):
                        skip = True
                        break
                
                if not skip:
                    files.append(str(file_path))
                    total_size += file_path.stat().st_size
            
            result.success = True
            result.files = files
            result.total_size = total_size
            result.metadata = {
                "repo_name": repo_name,
                "branch": branch,
                "cache_path": str(cache_path),
                "fetched_at": datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Fetched GitHub repo: {repo_url} ({len(files)} files)")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            result.errors.append(f"Git error: {error_msg}")
            logger.error(f"Git error for {repo_url}: {error_msg}")
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error fetching {repo_url}: {e}")
        
        return result.to_dict()
    
    def _parse_repo_name(self, url: str) -> Optional[str]:
        """Parse repository name from URL."""
        # Handle various GitHub URL formats
        url = url.rstrip("/")
        
        if url.endswith(".git"):
            url = url[:-4]
        
        # https://github.com/owner/repo
        # git@github.com:owner/repo
        if "github.com" in url:
            parts = url.split("github.com")[-1]
            parts = parts.lstrip("/").lstrip(":")
            if "/" in parts:
                return parts.replace("/", "_")
        
        return None
    
    async def _git_clone(
        self,
        repo_url: str,
        dest_path: Path,
        branch: str,
        depth: int,
    ):
        """Clone a repository."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["git", "clone", "--branch", branch]
        if depth > 0:
            cmd.extend(["--depth", str(depth)])
        
        # Add token authentication if available
        if self.github_token and "github.com" in repo_url:
            # Modify URL to include token
            if repo_url.startswith("https://"):
                repo_url = repo_url.replace(
                    "https://",
                    f"https://{self.github_token}@"
                )
        
        cmd.extend([repo_url, str(dest_path)])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=stderr,
            )
    
    async def _git_pull(self, repo_path: Path, branch: str):
        """Pull latest changes."""
        cmd = ["git", "pull", "origin", branch]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=stderr,
            )


class S3Fetcher(RemoteFetcher):
    """
    Fetcher for S3/MinIO object storage.
    
    Example:
        >>> fetcher = S3Fetcher(endpoint_url="http://localhost:9000")
        >>> result = await fetcher.fetch(
        ...     bucket="documents",
        ...     prefix="reports/",
        ... )
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize S3 fetcher.
        
        Args:
            config: Application configuration
            endpoint_url: S3/MinIO endpoint URL
            access_key: AWS access key ID
            secret_key: AWS secret access key
        """
        super().__init__(config)
        
        self.endpoint_url = endpoint_url
        self.access_key = access_key or os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        
        # Use MinIO config if available
        if self.config.minio.enabled and not endpoint_url:
            self.endpoint_url = f"http://{self.config.minio.endpoint}"
            self.access_key = self.access_key or self.config.minio.access_key
            self.secret_key = self.secret_key or self.config.minio.secret_key
    
    async def fetch(
        self,
        bucket: str,
        prefix: str = "",
        keys: Optional[List[str]] = None,
        max_files: int = 1000,
    ) -> Dict[str, Any]:
        """
        Fetch files from S3/MinIO.
        
        Args:
            bucket: S3 bucket name
            prefix: Key prefix (folder path)
            keys: Specific keys to fetch (empty = all in prefix)
            max_files: Maximum number of files to fetch
            
        Returns:
            FetchResult dictionary
        """
        result = FetchResult(source=f"s3://{bucket}/{prefix}", success=False)
        
        try:
            import boto3
            from botocore.config import Config
            
            # Create S3 client
            client_config = Config(
                signature_version="s3v4",
                retries={"max_attempts": 3},
            )
            
            client_kwargs = {
                "config": client_config,
            }
            
            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            if self.access_key:
                client_kwargs["aws_access_key_id"] = self.access_key
            if self.secret_key:
                client_kwargs["aws_secret_access_key"] = self.secret_key
            
            s3 = boto3.client("s3", **client_kwargs)
            
            # Determine keys to fetch
            if keys:
                keys_to_fetch = keys
            else:
                # List objects with prefix
                keys_to_fetch = []
                paginator = s3.get_paginator("list_objects_v2")
                
                for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                    for obj in page.get("Contents", []):
                        keys_to_fetch.append(obj["Key"])
                        if len(keys_to_fetch) >= max_files:
                            break
                    if len(keys_to_fetch) >= max_files:
                        break
            
            # Download files
            cache_path = self._cache_dir / "s3" / bucket
            cache_path.mkdir(parents=True, exist_ok=True)
            
            files = []
            total_size = 0
            
            for key in keys_to_fetch:
                try:
                    # Create local path
                    local_path = cache_path / key.replace("/", os.sep)
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download
                    s3.download_file(bucket, key, str(local_path))
                    
                    files.append(str(local_path))
                    total_size += local_path.stat().st_size
                    
                except Exception as e:
                    result.errors.append(f"Failed to download {key}: {str(e)}")
            
            result.success = len(files) > 0
            result.files = files
            result.total_size = total_size
            result.metadata = {
                "bucket": bucket,
                "prefix": prefix,
                "cache_path": str(cache_path),
                "fetched_at": datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Fetched {len(files)} files from s3://{bucket}/{prefix}")
            
        except ImportError:
            result.errors.append("boto3 is required for S3 support. Install with: pip install boto3")
            logger.error("boto3 not installed")
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error fetching from S3: {e}")
        
        return result.to_dict()


class WebCrawler(RemoteFetcher):
    """
    Web crawler for fetching multiple pages from a website.
    
    Example:
        >>> crawler = WebCrawler()
        >>> result = await crawler.fetch(
        ...     start_url="https://docs.example.com",
        ...     max_pages=50,
        ... )
    """
    
    async def fetch(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 3,
        same_domain_only: bool = True,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Crawl a website.
        
        Args:
            start_url: Starting URL
            max_pages: Maximum number of pages to fetch
            max_depth: Maximum crawl depth
            same_domain_only: Only crawl same domain
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            
        Returns:
            FetchResult dictionary
        """
        import httpx
        from urllib.parse import urljoin, urlparse
        
        result = FetchResult(source=start_url, success=False)
        
        try:
            visited = set()
            to_visit = [(start_url, 0)]  # (url, depth)
            files = []
            total_size = 0
            
            parsed_start = urlparse(start_url)
            start_domain = parsed_start.netloc
            
            exclude_patterns = exclude_patterns or []
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                while to_visit and len(files) < max_pages:
                    url, depth = to_visit.pop(0)
                    
                    if url in visited or depth > max_depth:
                        continue
                    
                    visited.add(url)
                    
                    # Check patterns
                    if include_patterns:
                        if not any(p in url for p in include_patterns):
                            continue
                    
                    if any(p in url for p in exclude_patterns):
                        continue
                    
                    try:
                        response = await client.get(url)
                        response.raise_for_status()
                        
                        content = response.content
                        content_type = response.headers.get("content-type", "")
                        
                        # Save page
                        cache_key = url.replace("/", "_").replace(":", "_")[:100]
                        
                        if "html" in content_type:
                            ext = ".html"
                        else:
                            ext = ".txt"
                        
                        file_path = self._cache_dir / "crawl" / f"{cache_key}{ext}"
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(file_path, "wb") as f:
                            f.write(content)
                        
                        files.append(str(file_path))
                        total_size += len(content)
                        
                        # Extract links if HTML
                        if "html" in content_type and depth < max_depth:
                            links = self._extract_links(content.decode("utf-8", errors="ignore"), url)
                            
                            for link in links:
                                parsed = urlparse(link)
                                
                                # Check domain
                                if same_domain_only and parsed.netloc != start_domain:
                                    continue
                                
                                if link not in visited:
                                    to_visit.append((link, depth + 1))
                        
                    except Exception as e:
                        result.errors.append(f"Error fetching {url}: {str(e)}")
            
            result.success = len(files) > 0
            result.files = files
            result.total_size = total_size
            result.metadata = {
                "pages_crawled": len(files),
                "max_pages": max_pages,
                "max_depth": max_depth,
                "fetched_at": datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Crawled {len(files)} pages from {start_url}")
            
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error crawling {start_url}: {e}")
        
        return result.to_dict()
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        from urllib.parse import urljoin
        import re
        
        links = []
        
        # Simple regex for href attributes
        href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
        
        for match in href_pattern.finditer(html):
            href = match.group(1)
            
            # Skip anchors, javascript, mailto
            if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            
            # Convert to absolute URL
            absolute = urljoin(base_url, href)
            
            # Only include http(s) URLs
            if absolute.startswith("http"):
                links.append(absolute)
        
        return links


# Factory function
def get_fetcher(source_type: str, **kwargs) -> RemoteFetcher:
    """
    Factory function to get appropriate fetcher.
    
    Args:
        source_type: Type of source (url, github, s3, crawl)
        **kwargs: Additional arguments for fetcher
        
    Returns:
        RemoteFetcher instance
    """
    fetchers = {
        "url": URLFetcher,
        "github": GitHubFetcher,
        "s3": S3Fetcher,
        "minio": S3Fetcher,
        "crawl": WebCrawler,
    }
    
    fetcher_class = fetchers.get(source_type.lower())
    if not fetcher_class:
        raise ValueError(f"Unknown source type: {source_type}. Available: {list(fetchers.keys())}")
    
    return fetcher_class(**kwargs)
