"""
Data Sources API Router.

This module provides REST endpoints for data source management:
- CRUD operations for data sources
- Connection testing
- Schema discovery
- Project-source linking
"""

from typing import Any, Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.data.sources import DataSourceManager, ConnectionResult
from agentic_assistants.data.catalog import DataCatalog
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/datasources", tags=["datasources"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DataSourceCreate(BaseModel):
    """Request to create a new data source."""
    name: str = Field(..., description="Data source name")
    source_type: str = Field(..., description="Source type (database, file_store, api)")
    connection_config: dict = Field(..., description="Connection configuration")
    description: str = Field(default="", description="Source description")
    is_global: bool = Field(default=False, description="Whether this is a global source")
    project_id: Optional[str] = Field(default=None, description="Project ID if project-scoped")
    tags: List[str] = Field(default_factory=list, description="Tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class DataSourceUpdate(BaseModel):
    """Request to update a data source."""
    name: Optional[str] = None
    connection_config: Optional[dict] = None
    description: Optional[str] = None
    is_global: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class DataSourceResponse(BaseModel):
    """Data source response model."""
    id: str
    name: str
    source_type: str
    connection_config: str
    description: str
    is_global: bool
    project_id: Optional[str]
    status: str
    last_tested: Optional[str]
    last_test_success: bool
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class DataSourcesListResponse(BaseModel):
    """Response containing list of data sources."""
    items: List[DataSourceResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class ConnectionTestResult(BaseModel):
    """Result of a connection test."""
    success: bool
    message: str
    latency_ms: Optional[float] = None
    details: dict = Field(default_factory=dict)


class SchemaResponse(BaseModel):
    """Response containing schema information."""
    source_id: str
    source_type: str
    tables: List[dict]
    discovered_at: str
    metadata: dict


class LinkResourceRequest(BaseModel):
    """Request to link a source to a project."""
    project_id: str = Field(..., description="Project ID to link to")
    alias: Optional[str] = Field(default=None, description="Optional project-local alias")
    config_overrides: dict = Field(default_factory=dict, description="Project-specific config overrides")


# ============================================================================
# Helper Functions
# ============================================================================

_manager: Optional[DataSourceManager] = None
_catalog: Optional[DataCatalog] = None


def get_manager() -> DataSourceManager:
    """Get the data source manager instance."""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager


def get_catalog() -> DataCatalog:
    """Get the data catalog instance."""
    global _catalog
    if _catalog is None:
        _catalog = DataCatalog()
    return _catalog


VALID_SOURCE_TYPES = {"database", "file_store", "api"}


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.get("", response_model=DataSourcesListResponse)
async def list_datasources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    is_global: Optional[bool] = Query(None, description="Filter by global status"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> DataSourcesListResponse:
    """List all data sources with optional filtering."""
    manager = get_manager()
    
    if source_type and source_type not in VALID_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source type. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"
        )
    
    sources, total = manager.list_sources(
        source_type=source_type,
        is_global=is_global,
        project_id=project_id,
        page=page,
        limit=limit,
    )
    
    return DataSourcesListResponse(
        items=[DataSourceResponse(**s.to_dict()) for s in sources],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=DataSourceResponse)
async def create_datasource(request: DataSourceCreate) -> DataSourceResponse:
    """Create a new data source."""
    manager = get_manager()
    
    if request.source_type not in VALID_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source type. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"
        )
    
    try:
        source = manager.create_source(
            name=request.name,
            source_type=request.source_type,
            connection_config=request.connection_config,
            description=request.description,
            is_global=request.is_global,
            project_id=request.project_id,
            tags=request.tags,
            metadata=request.metadata,
        )
        return DataSourceResponse(**source.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create datasource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_source_types() -> dict:
    """List all supported source types and their drivers."""
    manager = get_manager()
    return {
        "types": manager.list_supported_types(),
    }


@router.get("/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(datasource_id: str) -> DataSourceResponse:
    """Get a data source by ID."""
    manager = get_manager()
    source = manager.get_source(datasource_id)
    
    if source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse(**source.to_dict())


@router.put("/{datasource_id}", response_model=DataSourceResponse)
async def update_datasource(datasource_id: str, request: DataSourceUpdate) -> DataSourceResponse:
    """Update a data source."""
    manager = get_manager()
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    try:
        source = manager.update_source(datasource_id, **update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse(**source.to_dict())


@router.delete("/{datasource_id}")
async def delete_datasource(datasource_id: str) -> dict:
    """Delete a data source."""
    manager = get_manager()
    
    if not manager.delete_source(datasource_id):
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return {"status": "deleted", "id": datasource_id}


# ============================================================================
# Connection Testing
# ============================================================================

@router.post("/{datasource_id}/test", response_model=ConnectionTestResult)
async def test_connection(datasource_id: str) -> ConnectionTestResult:
    """Test connection for a data source."""
    manager = get_manager()
    
    result = manager.test_connection(datasource_id)
    
    return ConnectionTestResult(
        success=result.success,
        message=result.message,
        latency_ms=result.latency_ms,
        details=result.details,
    )


@router.post("/test", response_model=ConnectionTestResult)
async def test_connection_config(request: DataSourceCreate) -> ConnectionTestResult:
    """Test a connection configuration without creating a source."""
    manager = get_manager()
    
    handler = manager.get_handler(request.source_type)
    if not handler:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source type: {request.source_type}"
        )
    
    result = handler.test_connection(request.connection_config)
    
    return ConnectionTestResult(
        success=result.success,
        message=result.message,
        latency_ms=result.latency_ms,
        details=result.details,
    )


# ============================================================================
# Schema Discovery
# ============================================================================

@router.get("/{datasource_id}/schema", response_model=SchemaResponse)
async def get_schema(datasource_id: str) -> SchemaResponse:
    """Get schema information for a data source."""
    manager = get_manager()
    
    source = manager.get_source(datasource_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    schema = manager.discover_schema(source)
    
    return SchemaResponse(
        source_id=schema.source_id,
        source_type=schema.source_type,
        tables=[t.to_dict() for t in schema.tables],
        discovered_at=schema.discovered_at.isoformat(),
        metadata=schema.metadata,
    )


@router.post("/{datasource_id}/index")
async def index_datasource(
    datasource_id: str,
    force: bool = Query(False, description="Force re-indexing"),
) -> dict:
    """Index a data source into the catalog."""
    catalog = get_catalog()
    
    result = catalog.index_source(datasource_id, force=force)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# ============================================================================
# Project Integration
# ============================================================================

@router.post("/{datasource_id}/promote")
async def promote_to_global(datasource_id: str) -> DataSourceResponse:
    """Promote a project-scoped source to the global registry."""
    manager = get_manager()
    
    source = manager.promote_to_global(datasource_id)
    
    if source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse(**source.to_dict())


@router.post("/{datasource_id}/link")
async def link_to_project(datasource_id: str, request: LinkResourceRequest) -> dict:
    """Link a global source to a project."""
    manager = get_manager()
    
    success = manager.link_to_project(
        source_id=datasource_id,
        project_id=request.project_id,
        alias=request.alias,
        config_overrides=request.config_overrides,
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to link source. Source may not exist or is not global."
        )
    
    return {
        "status": "linked",
        "datasource_id": datasource_id,
        "project_id": request.project_id,
    }


@router.get("/project/{project_id}")
async def get_project_datasources(project_id: str) -> dict:
    """Get all data sources available to a project."""
    manager = get_manager()
    
    sources = manager.get_project_sources(project_id)
    
    return {
        "project_id": project_id,
        "datasources": [DataSourceResponse(**s.to_dict()) for s in sources],
        "count": len(sources),
    }


# ============================================================================
# Catalog Endpoints
# ============================================================================

@router.get("/catalog/search")
async def search_catalog(
    query: str = Query(..., description="Search query"),
    entry_type: Optional[str] = Query(None, description="Filter by entry type (table, column)"),
    source_id: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
) -> dict:
    """Search the data catalog."""
    catalog = get_catalog()
    
    result = catalog.search(
        query=query,
        entry_type=entry_type,
        source_id=source_id,
        limit=limit,
    )
    
    return {
        "entries": [e.to_dict() for e in result.entries],
        "total": result.total,
        "query": result.query,
        "filters": result.filters,
    }


@router.get("/catalog/stats")
async def get_catalog_stats() -> dict:
    """Get data catalog statistics."""
    catalog = get_catalog()
    return catalog.get_stats()



