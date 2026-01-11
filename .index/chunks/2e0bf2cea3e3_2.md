# Chunk: 2e0bf2cea3e3_2

- source: `src/agentic_assistants/data/datasets/api_dataset.py`
- lines: 157-242
- chunk: 3/5

```
mit")
        limit = self._pagination.get("limit", 100)
        max_pages = self._pagination.get("max_pages", 100)
        data_path = self._pagination.get("data_path", self._response_path)
        
        headers = self._setup_auth(self._headers)
        
        while page <= max_pages:
            params = {**self._params, page_param: page, limit_param: limit}
            
            response = client.request(
                method=self._method,
                url=self._url,
                headers=headers,
                params=params,
                json=self._request_body,
                **self._load_args,
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extract data using path
            if data_path:
                page_data = response_data
                for key in data_path.split("."):
                    if isinstance(page_data, dict):
                        page_data = page_data.get(key, [])
                    else:
                        break
            else:
                page_data = response_data
            
            if not page_data:
                break
            
            if isinstance(page_data, list):
                all_data.extend(page_data)
            else:
                all_data.append(page_data)
            
            # Check if we've reached the last page
            if len(page_data) < limit:
                break
            
            page += 1
        
        return all_data
    
    def _load(self) -> Union[Dict, List, str]:
        """Load data from API."""
        try:
            import httpx
        except ImportError:
            raise DatasetError("httpx not installed. Run: pip install httpx")
        
        # Check cache first
        if self._cache_filepath and Path(self._cache_filepath).exists():
            with open(self._cache_filepath, "r") as f:
                return json.load(f)
        
        with httpx.Client(**self._load_args) as client:
            if self._pagination:
                data = self._load_paginated(client)
            else:
                headers = self._setup_auth(self._headers)
                
                response = client.request(
                    method=self._method,
                    url=self._url,
                    headers=headers,
                    params=self._params,
                    json=self._request_body,
                )
                response.raise_for_status()
                
                # Handle different response types
                content_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    data = response.json()
                    data = self._extract_data(data)
                else:
                    data = response.text
        
```
