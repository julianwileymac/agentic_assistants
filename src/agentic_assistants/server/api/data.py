"""
Data Layer API Router.

This module provides REST endpoints for data layer operations:
- File read/write operations
- Table preview and pagination
- Schema inspection
- Cache management
"""

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.data.layer import DataLayer
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/data", tags=["data"])


# === Request/Response Models ===


class FileInfo(BaseModel):
    """Information about a file."""
    
    path: str = Field(..., description="File path")
    name: str = Field(..., description="File name")
    extension: str = Field(..., description="File extension")
    size: int = Field(0, description="File size in bytes")
    format: Optional[str] = Field(None, description="Detected format")
    is_dir: bool = Field(False, description="Whether it's a directory")
    modified_at: Optional[str] = Field(None, description="Last modified time")


class ColumnInfo(BaseModel):
    """Information about a table column."""
    
    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type")
    nullable: bool = Field(True, description="Whether column allows nulls")
    num_unique: Optional[int] = Field(None, description="Number of unique values")
    null_count: Optional[int] = Field(None, description="Count of null values")
    sample_values: list[Any] = Field(default_factory=list, description="Sample values")


class TableSchema(BaseModel):
    """Schema information for a table."""
    
    path: str = Field(..., description="File path")
    format: str = Field(..., description="File format")
    columns: list[ColumnInfo] = Field(default_factory=list, description="Column information")
    row_count: int = Field(0, description="Total row count")
    size_bytes: int = Field(0, description="File size in bytes")


class TablePreview(BaseModel):
    """Preview of table data."""
    
    path: str = Field(..., description="File path")
    columns: list[str] = Field(default_factory=list, description="Column names")
    rows: list[dict[str, Any]] = Field(default_factory=list, description="Row data")
    total_rows: int = Field(0, description="Total row count")
    offset: int = Field(0, description="Current offset")
    limit: int = Field(100, description="Current limit")


class WriteRequest(BaseModel):
    """Request to write data."""
    
    path: str = Field(..., description="Target file path")
    data: Any = Field(..., description="Data to write")
    format: Optional[str] = Field(None, description="Output format")


class CacheStats(BaseModel):
    """Cache statistics."""
    
    enabled: bool = Field(..., description="Whether cache is enabled")
    hits: int = Field(0, description="Cache hits")
    misses: int = Field(0, description="Cache misses")
    size: int = Field(0, description="Number of cached items")
    max_size: int = Field(100, description="Maximum cache size")


class DirectoryListing(BaseModel):
    """Directory listing response."""
    
    path: str = Field(..., description="Directory path")
    files: list[FileInfo] = Field(default_factory=list, description="Files in directory")
    total: int = Field(0, description="Total file count")


# === Helper Functions ===


_data_layer: Optional[DataLayer] = None


def get_data_layer() -> DataLayer:
    """Get the data layer instance."""
    global _data_layer
    if _data_layer is None:
        _data_layer = DataLayer()
    return _data_layer


def _get_file_info(path: Path) -> FileInfo:
    """Get file information."""
    from datetime import datetime
    
    stat = path.stat() if path.exists() else None
    
    format_map = {
        ".parquet": "parquet",
        ".pq": "parquet",
        ".json": "json",
        ".jsonl": "jsonl",
        ".csv": "csv",
        ".txt": "text",
        ".md": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
    }
    
    return FileInfo(
        path=str(path),
        name=path.name,
        extension=path.suffix,
        size=stat.st_size if stat else 0,
        format=format_map.get(path.suffix.lower()),
        is_dir=path.is_dir(),
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat() if stat else None,
    )


def _table_to_preview(
    table,
    path: str,
    offset: int = 0,
    limit: int = 100,
) -> TablePreview:
    """Convert PyArrow table to preview."""
    import pyarrow as pa
    
    if not isinstance(table, pa.Table):
        raise ValueError("Expected PyArrow Table")
    
    total_rows = table.num_rows
    
    # Slice table for preview
    end = min(offset + limit, total_rows)
    sliced = table.slice(offset, end - offset)
    
    # Convert to rows
    rows = []
    for i in range(sliced.num_rows):
        row = {}
        for col_name in sliced.column_names:
            value = sliced.column(col_name)[i].as_py()
            row[col_name] = value
        rows.append(row)
    
    return TablePreview(
        path=path,
        columns=table.column_names,
        rows=rows,
        total_rows=total_rows,
        offset=offset,
        limit=limit,
    )


def _get_table_schema(table, path: str) -> TableSchema:
    """Get schema information from PyArrow table."""
    import pyarrow as pa
    
    if not isinstance(table, pa.Table):
        raise ValueError("Expected PyArrow Table")
    
    columns = []
    for i, field in enumerate(table.schema):
        col = table.column(i)
        
        # Get sample values
        samples = []
        for j in range(min(5, len(col))):
            samples.append(col[j].as_py())
        
        columns.append(ColumnInfo(
            name=field.name,
            dtype=str(field.type),
            nullable=field.nullable,
            num_unique=col.unique().length() if hasattr(col, 'unique') else None,
            null_count=col.null_count,
            sample_values=samples,
        ))
    
    return TableSchema(
        path=path,
        format="parquet",
        columns=columns,
        row_count=table.num_rows,
        size_bytes=table.nbytes,
    )


# === Endpoints ===


@router.get("/files", response_model=DirectoryListing)
async def list_files(
    path: str = Query(".", description="Directory path"),
    pattern: str = Query("*", description="Glob pattern"),
) -> DirectoryListing:
    """List files in a directory."""
    logger.debug(f"Listing files in: {path}")
    
    config = AgenticConfig()
    base_path = Path(config.data_dir)
    target_path = base_path / path if not Path(path).is_absolute() else Path(path)
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Directory not found")
    
    if not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    files = []
    for item in target_path.glob(pattern):
        files.append(_get_file_info(item))
    
    return DirectoryListing(
        path=str(target_path),
        files=files,
        total=len(files),
    )


@router.get("/file", response_model=FileInfo)
async def get_file_info(path: str = Query(..., description="File path")) -> FileInfo:
    """Get information about a file."""
    logger.debug(f"Getting file info: {path}")
    
    file_path = Path(path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return _get_file_info(file_path)


@router.get("/read")
async def read_file(
    path: str = Query(..., description="File path"),
    format: Optional[str] = Query(None, description="Override format detection"),
) -> dict[str, Any]:
    """Read a file and return its contents."""
    logger.debug(f"Reading file: {path}")
    
    layer = get_data_layer()
    file_path = Path(path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        data = layer.read(file_path, format=format)
        
        # Convert PyArrow tables to dict for JSON serialization
        import pyarrow as pa
        if isinstance(data, pa.Table):
            return {
                "path": str(file_path),
                "format": format or layer._get_format(file_path),
                "type": "table",
                "columns": data.column_names,
                "row_count": data.num_rows,
                "data": data.to_pydict(),
            }
        
        return {
            "path": str(file_path),
            "format": format or layer._get_format(file_path),
            "type": type(data).__name__,
            "data": data,
        }
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write")
async def write_file(request: WriteRequest) -> dict[str, str]:
    """Write data to a file."""
    logger.info(f"Writing file: {request.path}")
    
    layer = get_data_layer()
    
    try:
        result_path = layer.write(
            request.data,
            request.path,
            format=request.format,
        )
        
        return {
            "status": "written",
            "path": str(result_path),
        }
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file")
async def delete_file(path: str = Query(..., description="File path")) -> dict[str, str]:
    """Delete a file."""
    logger.info(f"Deleting file: {path}")
    
    layer = get_data_layer()
    
    if layer.delete(path):
        return {"status": "deleted", "path": path}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.get("/schema", response_model=TableSchema)
async def get_schema(path: str = Query(..., description="File path")) -> TableSchema:
    """Get schema information for a tabular file."""
    logger.debug(f"Getting schema for: {path}")
    
    layer = get_data_layer()
    file_path = Path(path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        data = layer.read(file_path)
        
        import pyarrow as pa
        if not isinstance(data, pa.Table):
            raise HTTPException(
                status_code=400,
                detail="File is not a tabular format (parquet/csv)"
            )
        
        return _get_table_schema(data, str(file_path))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview", response_model=TablePreview)
async def preview_table(
    path: str = Query(..., description="File path"),
    offset: int = Query(0, ge=0, description="Row offset"),
    limit: int = Query(100, ge=1, le=1000, description="Row limit"),
) -> TablePreview:
    """Get a paginated preview of a tabular file."""
    logger.debug(f"Previewing table: {path} (offset={offset}, limit={limit})")
    
    layer = get_data_layer()
    file_path = Path(path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        data = layer.read(file_path)
        
        import pyarrow as pa
        if not isinstance(data, pa.Table):
            raise HTTPException(
                status_code=400,
                detail="File is not a tabular format (parquet/csv)"
            )
        
        return _table_to_preview(data, str(file_path), offset, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
async def query_table(
    path: str = Query(..., description="File path"),
    columns: Optional[str] = Query(None, description="Comma-separated columns to select"),
    filter_expr: Optional[str] = Query(None, description="Filter expression"),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    ascending: bool = Query(True, description="Sort order"),
    limit: int = Query(100, ge=1, le=10000, description="Row limit"),
) -> dict[str, Any]:
    """Query a tabular file with filtering and sorting."""
    logger.debug(f"Querying table: {path}")
    
    layer = get_data_layer()
    file_path = Path(path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        import pyarrow as pa
        import pyarrow.compute as pc
        
        data = layer.read(file_path)
        
        if not isinstance(data, pa.Table):
            raise HTTPException(
                status_code=400,
                detail="File is not a tabular format"
            )
        
        # Select columns
        if columns:
            col_list = [c.strip() for c in columns.split(",")]
            data = data.select(col_list)
        
        # Apply filter (basic support)
        # Note: Full filter expression parsing would require more complex implementation
        if filter_expr:
            logger.warning("Filter expressions are limited in this version")
        
        # Sort
        if sort_by and sort_by in data.column_names:
            indices = pc.sort_indices(data, sort_keys=[(sort_by, "ascending" if ascending else "descending")])
            data = data.take(indices)
        
        # Limit
        data = data.slice(0, limit)
        
        return {
            "path": str(file_path),
            "columns": data.column_names,
            "row_count": data.num_rows,
            "data": data.to_pydict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats() -> CacheStats:
    """Get data layer cache statistics."""
    logger.debug("Getting cache stats")
    
    layer = get_data_layer()
    stats = layer.get_cache_stats()
    
    if stats is None:
        return CacheStats(
            enabled=False,
            hits=0,
            misses=0,
            size=0,
            max_size=0,
        )
    
    return CacheStats(
        enabled=True,
        hits=stats.get("hits", 0),
        misses=stats.get("misses", 0),
        size=stats.get("size", 0),
        max_size=stats.get("max_size", 100),
    )


@router.post("/cache/clear")
async def clear_cache() -> dict[str, str]:
    """Clear the data layer cache."""
    logger.info("Clearing data layer cache")
    
    layer = get_data_layer()
    layer.clear_cache()
    
    return {"status": "cleared"}


@router.post("/convert")
async def convert_file(
    source_path: str = Query(..., description="Source file path"),
    target_path: str = Query(..., description="Target file path"),
    target_format: Optional[str] = Query(None, description="Target format"),
) -> dict[str, str]:
    """Convert a file to another format."""
    logger.info(f"Converting {source_path} to {target_path}")
    
    layer = get_data_layer()
    
    source = Path(source_path)
    if not source.exists():
        raise HTTPException(status_code=404, detail="Source file not found")
    
    try:
        data = layer.read(source)
        result = layer.write(data, target_path, format=target_format)
        
        return {
            "status": "converted",
            "source": source_path,
            "target": str(result),
        }
    except Exception as e:
        logger.error(f"Failed to convert file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-formats")
async def get_supported_formats() -> dict[str, Any]:
    """Get list of supported file formats."""
    return {
        "formats": {
            "parquet": {
                "extensions": [".parquet", ".pq"],
                "description": "Apache Parquet columnar format",
                "read": True,
                "write": True,
            },
            "json": {
                "extensions": [".json"],
                "description": "JSON format",
                "read": True,
                "write": True,
            },
            "jsonl": {
                "extensions": [".jsonl"],
                "description": "JSON Lines format",
                "read": True,
                "write": True,
            },
            "csv": {
                "extensions": [".csv"],
                "description": "Comma-separated values",
                "read": True,
                "write": True,
            },
            "text": {
                "extensions": [".txt", ".md", ".py"],
                "description": "Plain text",
                "read": True,
                "write": True,
            },
            "yaml": {
                "extensions": [".yaml", ".yml"],
                "description": "YAML format",
                "read": True,
                "write": True,
            },
        }
    }

