# Chunk: 2e0bf2cea3e3_0

- source: `src/agentic_assistants/data/datasets/api_dataset.py`
- lines: 1-97
- chunk: 1/5

```
"""
API dataset implementation for REST API data fetching.

This module provides a dataset type for loading data from REST APIs
with support for authentication, pagination, and caching.

Example:
    >>> from agentic_assistants.data.datasets import APIDataset
    >>> 
    >>> dataset = APIDataset(
    ...     url="https://api.example.com/users",
    ...     headers={"Authorization": "Bearer token"},
    ... )
    >>> data = dataset.load()
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from agentic_assistants.data.datasets.base import (
    AbstractDataset,
    DatasetError,
    DatasetMetadata,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class APIDataset(AbstractDataset[Union[Dict, List, str]]):
    """
    Dataset for REST API endpoints.
    
    Supports:
    - GET/POST/PUT/DELETE methods
    - Authentication (Bearer, API Key, Basic)
    - Pagination
    - Response caching
    - Retry logic
    
    Example:
        >>> # Simple GET request
        >>> dataset = APIDataset(url="https://api.example.com/data")
        >>> data = dataset.load()
        >>> 
        >>> # POST with body
        >>> dataset = APIDataset(
        ...     url="https://api.example.com/submit",
        ...     method="POST",
        ...     request_body={"key": "value"},
        ... )
    """
    
    DEFAULT_LOAD_ARGS: Dict[str, Any] = {
        "timeout": 30,
        "verify": True,
    }
    
    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        auth_type: Optional[str] = None,
        auth_config: Optional[Dict[str, str]] = None,
        response_path: Optional[str] = None,
        pagination: Optional[Dict[str, Any]] = None,
        cache_filepath: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize APIDataset.
        
        Args:
            url: Base URL for the API endpoint
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: HTTP headers to include
            params: Query parameters
            request_body: Request body for POST/PUT
            auth_type: Authentication type ('bearer', 'api_key', 'basic')
            auth_config: Authentication configuration
            response_path: JSON path to extract data from response
            pagination: Pagination configuration
            cache_filepath: Path to cache responses
            **kwargs: Additional arguments passed to parent
        """
        # Use URL as filepath for base class
        super().__init__(
            filepath=cache_filepath or url.replace("://", "_").replace("/", "_"),
            **kwargs,
        )
        
```
