# Chunk: 2e0bf2cea3e3_1

- source: `src/agentic_assistants/data/datasets/api_dataset.py`
- lines: 88-165
- chunk: 2/5

```
 Path to cache responses
            **kwargs: Additional arguments passed to parent
        """
        # Use URL as filepath for base class
        super().__init__(
            filepath=cache_filepath or url.replace("://", "_").replace("/", "_"),
            **kwargs,
        )
        
        self._url = url
        self._method = method.upper()
        self._headers = headers or {}
        self._params = params or {}
        self._request_body = request_body
        self._auth_type = auth_type
        self._auth_config = auth_config or {}
        self._response_path = response_path
        self._pagination = pagination
        self._cache_filepath = cache_filepath
    
    def _setup_auth(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Set up authentication headers."""
        if not self._auth_type:
            return headers
        
        headers = headers.copy()
        
        if self._auth_type == "bearer":
            token = self._auth_config.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        
        elif self._auth_type == "api_key":
            key_name = self._auth_config.get("header", "X-API-Key")
            key_value = self._auth_config.get("key", "")
            headers[key_name] = key_value
        
        elif self._auth_type == "basic":
            import base64
            username = self._auth_config.get("username", "")
            password = self._auth_config.get("password", "")
            credentials = base64.b64encode(
                f"{username}:{password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        return headers
    
    def _extract_data(self, response_data: Any) -> Any:
        """Extract data from response using JSON path."""
        if not self._response_path:
            return response_data
        
        # Simple dot-notation path extraction
        data = response_data
        for key in self._response_path.split("."):
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list) and key.isdigit():
                data = data[int(key)]
            else:
                return response_data
        
        return data
    
    def _load_paginated(self, client) -> List[Any]:
        """Load data with pagination."""
        all_data = []
        page = self._pagination.get("start_page", 1)
        page_param = self._pagination.get("page_param", "page")
        limit_param = self._pagination.get("limit_param", "limit")
        limit = self._pagination.get("limit", 100)
        max_pages = self._pagination.get("max_pages", 100)
        data_path = self._pagination.get("data_path", self._response_path)
        
        headers = self._setup_auth(self._headers)
        
        while page <= max_pages:
```
