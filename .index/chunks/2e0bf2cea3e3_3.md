# Chunk: 2e0bf2cea3e3_3

- source: `src/agentic_assistants/data/datasets/api_dataset.py`
- lines: 234-326
- chunk: 4/5

```
tent_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    data = response.json()
                    data = self._extract_data(data)
                else:
                    data = response.text
        
        # Cache response
        if self._cache_filepath:
            Path(self._cache_filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_filepath, "w") as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def _save(self, data: Any) -> None:
        """Save data via POST/PUT request."""
        try:
            import httpx
        except ImportError:
            raise DatasetError("httpx not installed. Run: pip install httpx")
        
        if self._method not in ("POST", "PUT", "PATCH"):
            raise DatasetError(
                f"Cannot save with {self._method} method. Use POST, PUT, or PATCH."
            )
        
        headers = self._setup_auth(self._headers)
        
        with httpx.Client(**self._load_args) as client:
            response = client.request(
                method=self._method,
                url=self._url,
                headers=headers,
                params=self._params,
                json=data,
            )
            response.raise_for_status()
    
    def exists(self) -> bool:
        """Check if the API endpoint is accessible."""
        try:
            import httpx
            
            with httpx.Client(timeout=5) as client:
                headers = self._setup_auth(self._headers)
                response = client.head(self._url, headers=headers)
                return response.status_code < 400
        except Exception:
            return False
    
    def _describe(self) -> Dict[str, Any]:
        """Describe the dataset configuration."""
        return {
            "url": self._url,
            "method": self._method,
            "auth_type": self._auth_type,
            "paginated": self._pagination is not None,
            "cached": self._cache_filepath is not None,
        }


class GraphQLDataset(APIDataset):
    """
    Dataset for GraphQL API endpoints.
    
    Example:
        >>> dataset = GraphQLDataset(
        ...     url="https://api.example.com/graphql",
        ...     query=\"\"\"
        ...         query GetUsers($limit: Int!) {
        ...             users(limit: $limit) {
        ...                 id
        ...                 name
        ...             }
        ...         }
        ...     \"\"\",
        ...     variables={"limit": 100},
        ... )
        >>> data = dataset.load()
    """
    
    def __init__(
        self,
        url: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **kwargs,
    ):
        """
```
