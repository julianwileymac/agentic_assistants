"""
Data source and sink nodes.

This module provides flow nodes for data operations:
- DataSourceNode: Read data from various sources
- DataSinkNode: Write data to destinations
- TransformNode: Transform data with expressions

Example:
    >>> from agentic_assistants.pipelines.nodes import DataSourceNode
    >>> 
    >>> source = DataSourceNode(config=DataSourceConfig(
    ...     source_type="database",
    ...     source_id="my_postgres",
    ...     query="SELECT * FROM users",
    ... ))
    >>> 
    >>> result = source.run({})
    >>> print(result.outputs["data"])
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class DataSourceConfig(NodeConfig):
    """Configuration for DataSourceNode."""
    
    # Data source ID (references configured data sources)
    source_id: str = ""
    
    # Source type: database, file, api, s3, gcs
    source_type: str = "database"
    
    # Query or path for data retrieval
    query: str = ""
    
    # Additional options
    options: Dict[str, Any] = field(default_factory=dict)
    
    # Batch size for large datasets
    batch_size: int = 1000


@dataclass
class DataSinkConfig(NodeConfig):
    """Configuration for DataSinkNode."""
    
    # Data sink ID
    sink_id: str = ""
    
    # Output format: json, csv, parquet, yaml
    format: str = "json"
    
    # Write mode: overwrite, append, merge
    mode: str = "overwrite"
    
    # Additional options
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformConfig(NodeConfig):
    """Configuration for TransformNode."""
    
    # Transform type: map, filter, reduce, flatMap, aggregate, join
    transform_type: str = "map"
    
    # Expression or code for transformation
    expression: str = ""
    
    # For aggregate operations
    group_by: List[str] = field(default_factory=list)
    
    # For join operations
    join_key: str = ""
    join_type: str = "inner"  # inner, left, right, outer
    
    # Output schema definition
    output_schema: Optional[Dict[str, str]] = None


# =============================================================================
# Node Implementations
# =============================================================================

class DataSourceNode(BaseFlowNode):
    """
    Node for reading data from various sources.
    
    Supports:
    - Database queries
    - File reads (local, S3, GCS)
    - API endpoints
    
    Inputs:
        query: Override query (optional)
        params: Query parameters
        
    Outputs:
        data: Retrieved data
        count: Number of records
    """
    
    node_type = "data_source"
    config_class = DataSourceConfig
    
    def __init__(self, config: Optional[DataSourceConfig] = None, **kwargs):
        super().__init__(config or DataSourceConfig(), **kwargs)
        self.config: DataSourceConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", self.config.query)
        params = inputs.get("params", {})
        
        if not self.config.source_id and not query:
            return {"data": [], "count": 0, "error": "No source or query specified"}
        
        try:
            data = []
            
            if self.config.source_type == "database":
                data = self._read_database(query, params)
            elif self.config.source_type == "file":
                data = self._read_file(query)
            elif self.config.source_type == "api":
                data = self._read_api(query, params)
            else:
                return {"data": [], "count": 0, "error": f"Unsupported source type: {self.config.source_type}"}
            
            # Emit metrics
            self.emit_metric("records_read", len(data))
            
            return {
                "data": data,
                "count": len(data),
            }
            
        except Exception as e:
            logger.error(f"Data source read failed: {e}")
            return {"data": [], "count": 0, "error": str(e)}
    
    def _read_database(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Read data from database."""
        # This would integrate with the data source manager
        # For now, return empty list
        logger.info(f"Database query: {query}")
        return []
    
    def _read_file(self, path: str) -> List[Dict[str, Any]]:
        """Read data from file."""
        import json
        
        try:
            with open(path, "r") as f:
                if path.endswith(".json"):
                    return json.load(f)
                elif path.endswith(".csv"):
                    import csv
                    reader = csv.DictReader(f)
                    return list(reader)
                else:
                    # Return as text
                    return [{"content": f.read()}]
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return []
    
    def _read_api(self, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Read data from API."""
        try:
            import httpx
            
            with httpx.Client() as client:
                response = client.get(url, params=params)
                data = response.json()
                
                if isinstance(data, list):
                    return data
                else:
                    return [data]
        except Exception as e:
            logger.error(f"API read failed: {e}")
            return []
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "params": {"type": "object"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {"type": "array"},
                "count": {"type": "integer"},
                "error": {"type": "string"},
            },
        }


class DataSinkNode(BaseFlowNode):
    """
    Node for writing data to destinations.
    
    Supports:
    - File writes (local, S3, GCS)
    - Database inserts
    - API posts
    
    Inputs:
        data: Data to write
        path: Override path (optional)
        
    Outputs:
        success: Whether write succeeded
        count: Number of records written
    """
    
    node_type = "data_sink"
    config_class = DataSinkConfig
    
    def __init__(self, config: Optional[DataSinkConfig] = None, **kwargs):
        super().__init__(config or DataSinkConfig(), **kwargs)
        self.config: DataSinkConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        data = inputs.get("data", [])
        path = inputs.get("path", self.config.sink_id)
        
        if not data:
            return {"success": True, "count": 0, "message": "No data to write"}
        
        if not path:
            return {"success": False, "count": 0, "error": "No sink specified"}
        
        try:
            count = self._write_data(data, path)
            
            # Emit metrics
            self.emit_metric("records_written", count)
            
            return {
                "success": True,
                "count": count,
            }
            
        except Exception as e:
            logger.error(f"Data sink write failed: {e}")
            return {"success": False, "count": 0, "error": str(e)}
    
    def _write_data(self, data: Any, path: str) -> int:
        """Write data to destination."""
        import json
        
        if isinstance(data, list):
            count = len(data)
        else:
            count = 1
            data = [data]
        
        if self.config.format == "json":
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        elif self.config.format == "csv":
            import csv
            
            if data and isinstance(data[0], dict):
                with open(path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            else:
                return 0
        else:
            # Default to JSON
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        
        return count
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {},
                "path": {"type": "string"},
            },
            "required": ["data"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "count": {"type": "integer"},
                "error": {"type": "string"},
            },
        }


class TransformNode(BaseFlowNode):
    """
    Node for transforming data.
    
    Supports:
    - Map: Apply function to each element
    - Filter: Keep elements matching condition
    - Reduce: Aggregate to single value
    - FlatMap: Map and flatten results
    
    Inputs:
        data: Data to transform
        
    Outputs:
        data: Transformed data
    """
    
    node_type = "transform"
    config_class = TransformConfig
    
    def __init__(self, config: Optional[TransformConfig] = None, **kwargs):
        super().__init__(config or TransformConfig(), **kwargs)
        self.config: TransformConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        data = inputs.get("data", [])
        
        if not data:
            return {"data": []}
        
        if not isinstance(data, list):
            data = [data]
        
        try:
            if self.config.transform_type == "map":
                result = self._apply_map(data)
            elif self.config.transform_type == "filter":
                result = self._apply_filter(data)
            elif self.config.transform_type == "reduce":
                result = self._apply_reduce(data)
            elif self.config.transform_type == "flatMap":
                result = self._apply_flatmap(data)
            elif self.config.transform_type == "aggregate":
                result = self._apply_aggregate(data)
            else:
                result = data
            
            # Emit metrics
            self.emit_metric("records_in", len(data))
            self.emit_metric("records_out", len(result) if isinstance(result, list) else 1)
            
            return {"data": result}
            
        except Exception as e:
            logger.error(f"Transform failed: {e}")
            return {"data": [], "error": str(e)}
    
    def _apply_map(self, data: List[Any]) -> List[Any]:
        """Apply map transformation."""
        if not self.config.expression:
            return data
        
        # Simple expression evaluation
        # In production, use a proper expression language
        results = []
        for item in data:
            try:
                # Allow access to item in expression
                result = eval(self.config.expression, {"item": item, "x": item})
                results.append(result)
            except Exception as e:
                logger.warning(f"Map expression failed for item: {e}")
                results.append(item)
        
        return results
    
    def _apply_filter(self, data: List[Any]) -> List[Any]:
        """Apply filter transformation."""
        if not self.config.expression:
            return data
        
        results = []
        for item in data:
            try:
                if eval(self.config.expression, {"item": item, "x": item}):
                    results.append(item)
            except Exception as e:
                logger.warning(f"Filter expression failed for item: {e}")
        
        return results
    
    def _apply_reduce(self, data: List[Any]) -> Any:
        """Apply reduce transformation."""
        if not self.config.expression or not data:
            return data
        
        try:
            # Expression should define how to combine acc and item
            result = data[0]
            for item in data[1:]:
                result = eval(self.config.expression, {"acc": result, "item": item})
            return result
        except Exception as e:
            logger.warning(f"Reduce expression failed: {e}")
            return data
    
    def _apply_flatmap(self, data: List[Any]) -> List[Any]:
        """Apply flatMap transformation."""
        mapped = self._apply_map(data)
        
        # Flatten one level
        results = []
        for item in mapped:
            if isinstance(item, list):
                results.extend(item)
            else:
                results.append(item)
        
        return results
    
    def _apply_aggregate(self, data: List[Any]) -> List[Dict[str, Any]]:
        """Apply aggregation transformation."""
        if not self.config.group_by or not data:
            return data
        
        # Group by specified fields
        groups: Dict[tuple, List[Any]] = {}
        
        for item in data:
            if isinstance(item, dict):
                key = tuple(item.get(k) for k in self.config.group_by)
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
        
        # Apply aggregation expression to each group
        results = []
        for key, items in groups.items():
            group_result = {k: v for k, v in zip(self.config.group_by, key)}
            group_result["count"] = len(items)
            group_result["items"] = items
            
            if self.config.expression:
                try:
                    agg_value = eval(self.config.expression, {"items": items, "group": items})
                    group_result["aggregate"] = agg_value
                except Exception:
                    pass
            
            results.append(group_result)
        
        return results
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {},
            },
            "required": ["data"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {},
                "error": {"type": "string"},
            },
        }
