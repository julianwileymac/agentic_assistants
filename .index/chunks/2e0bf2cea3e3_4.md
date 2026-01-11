# Chunk: 2e0bf2cea3e3_4

- source: `src/agentic_assistants/data/datasets/api_dataset.py`
- lines: 312-360
- chunk: 5/5

```
les={"limit": 100},
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
        Initialize GraphQLDataset.
        
        Args:
            url: GraphQL endpoint URL
            query: GraphQL query string
            variables: Query variables
            operation_name: Optional operation name
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(
            url=url,
            method="POST",
            request_body={
                "query": query,
                "variables": variables or {},
                "operationName": operation_name,
            },
            **kwargs,
        )
        self._query = query
        self._variables = variables
        self._operation_name = operation_name
    
    def _load(self) -> Dict:
        """Execute GraphQL query."""
        data = super()._load()
        
        # GraphQL responses have a standard structure
        if isinstance(data, dict):
            if "errors" in data and data["errors"]:
                raise DatasetError(f"GraphQL errors: {data['errors']}")
            return data.get("data", data)
        
        return data
```
