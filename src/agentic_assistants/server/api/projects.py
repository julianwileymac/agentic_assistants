"""
Projects API Router.

This module provides REST endpoints for project management including:
- CRUD operations for projects
- Git configuration management
- Service resource management
- Indexing state management
- Project resource linking
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.config import ProjectSettings, GitConfig, ServiceConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


# === Request/Response Models ===

class ProjectCreate(BaseModel):
    """Request to create a new project."""
    name: str = Field(..., description="Project name")
    description: str = Field(default="", description="Project description")
    config_yaml: str = Field(default="", description="Project configuration in YAML")
    status: str = Field(default="active", description="Project status")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ProjectUpdate(BaseModel):
    """Request to update a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    config_yaml: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ProjectResponse(BaseModel):
    """Project response model."""
    id: str
    name: str
    description: str
    config_yaml: str
    status: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class ProjectsListResponse(BaseModel):
    """Response containing list of projects."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# === Git Configuration Models ===

class GitConfigRequest(BaseModel):
    """Request to configure git for a project."""
    remote_url: Optional[str] = Field(default=None, description="Git remote URL")
    branch: str = Field(default="main", description="Default branch")
    auto_sync: bool = Field(default=False, description="Enable auto sync")
    ssh_key_ref: Optional[str] = Field(default=None, description="SSH key reference")


class GitConfigResponse(BaseModel):
    """Git configuration response."""
    project_id: str
    remote_url: Optional[str]
    branch: str
    auto_sync: bool
    ssh_key_ref: Optional[str]


# === Service Resource Models ===

class ServiceCreate(BaseModel):
    """Request to create a service resource."""
    name: str = Field(..., description="Service name")
    service_type: str = Field(..., description="Service type (web_ui, api_endpoint, file_store, background_service, database, ml_deployment)")
    endpoint_url: str = Field(default="", description="Service endpoint URL")
    description: str = Field(default="", description="Service description")
    health_endpoint: Optional[str] = Field(default=None, description="Health check endpoint")
    auth_type: Optional[str] = Field(default=None, description="Authentication type")
    credentials_ref: Optional[str] = Field(default=None, description="Credentials reference")
    config_yaml: str = Field(default="", description="Additional configuration")
    is_global: bool = Field(default=False, description="Is this a global service")
    tags: List[str] = Field(default_factory=list, description="Tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ServiceUpdate(BaseModel):
    """Request to update a service resource."""
    name: Optional[str] = None
    endpoint_url: Optional[str] = None
    description: Optional[str] = None
    health_endpoint: Optional[str] = None
    auth_type: Optional[str] = None
    credentials_ref: Optional[str] = None
    config_yaml: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ServiceResponse(BaseModel):
    """Service resource response model."""
    id: str
    name: str
    service_type: str
    endpoint_url: str
    description: str
    health_endpoint: Optional[str]
    auth_type: Optional[str]
    credentials_ref: Optional[str]
    config_yaml: str
    is_global: bool
    project_id: Optional[str]
    status: str
    last_health_check: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class ServicesListResponse(BaseModel):
    """Response containing list of services."""
    items: List[ServiceResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# === Indexing Models ===

class IndexingStateResponse(BaseModel):
    """Indexing state response model."""
    id: str
    project_id: str
    collection_name: str
    version: str
    status: str
    file_count: int
    chunk_count: int
    last_indexed: Optional[str]
    error_message: Optional[str]
    created_at: str
    updated_at: str


class IndexRequest(BaseModel):
    """Request to trigger indexing."""
    force: bool = Field(default=False, description="Force re-index even if up to date")
    path: Optional[str] = Field(default=None, description="Specific path to index")


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


# === Endpoints ===

@router.get("", response_model=ProjectsListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> ProjectsListResponse:
    """List all projects with optional filtering."""
    store = _get_store()
    projects, total = store.list_projects(status=status, page=page, limit=limit)
    
    return ProjectsListResponse(
        items=[ProjectResponse(**p.to_dict()) for p in projects],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=ProjectResponse)
async def create_project(request: ProjectCreate) -> ProjectResponse:
    """Create a new project."""
    store = _get_store()
    
    try:
        project = store.create_project(
            name=request.name,
            description=request.description,
            config_yaml=request.config_yaml,
            status=request.status,
            tags=request.tags,
            metadata=request.metadata,
        )
        return ProjectResponse(**project.to_dict())
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    """Get a project by ID."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project.to_dict())


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, request: ProjectUpdate) -> ProjectResponse:
    """Update a project."""
    store = _get_store()
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    project = store.update_project(project_id, **update_data)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project.to_dict())


@router.delete("/{project_id}")
async def delete_project(project_id: str) -> dict:
    """Delete a project."""
    store = _get_store()
    
    if not store.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"status": "deleted", "id": project_id}


# === Git Configuration Endpoints ===

@router.get("/{project_id}/git", response_model=GitConfigResponse)
async def get_git_config(project_id: str) -> GitConfigResponse:
    """Get git configuration for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Load project settings
    from pathlib import Path
    settings = ProjectSettings.load_for_project(project_id, Path("./data/projects"))
    
    return GitConfigResponse(
        project_id=project_id,
        remote_url=settings.git.remote_url if settings.git else None,
        branch=settings.git.branch if settings.git else "main",
        auto_sync=settings.git.auto_sync if settings.git else False,
        ssh_key_ref=settings.git.ssh_key_ref if settings.git else None,
    )


@router.put("/{project_id}/git", response_model=GitConfigResponse)
async def update_git_config(project_id: str, request: GitConfigRequest) -> GitConfigResponse:
    """Update git configuration for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Load and update project settings
    from pathlib import Path
    settings = ProjectSettings.load_for_project(project_id, Path("./data/projects"))
    
    settings.git = GitConfig(
        remote_url=request.remote_url,
        branch=request.branch,
        auto_sync=request.auto_sync,
        ssh_key_ref=request.ssh_key_ref,
    )
    settings.save(Path("./data/projects"))
    
    return GitConfigResponse(
        project_id=project_id,
        remote_url=settings.git.remote_url,
        branch=settings.git.branch,
        auto_sync=settings.git.auto_sync,
        ssh_key_ref=settings.git.ssh_key_ref,
    )


@router.post("/{project_id}/git/sync")
async def sync_git(project_id: str) -> dict:
    """Trigger git sync for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Load project settings
    from pathlib import Path
    settings = ProjectSettings.load_for_project(project_id, Path("./data/projects"))
    
    if not settings.git or not settings.git.remote_url:
        raise HTTPException(status_code=400, detail="Git not configured for this project")
    
    # TODO: Implement actual git sync logic
    # For now, return a placeholder response
    return {
        "status": "synced",
        "project_id": project_id,
        "remote_url": settings.git.remote_url,
        "branch": settings.git.branch,
    }


# === Service Resource Endpoints ===

VALID_SERVICE_TYPES = {"web_ui", "api_endpoint", "file_store", "background_service", "database", "ml_deployment"}


@router.get("/{project_id}/services", response_model=ServicesListResponse)
async def list_project_services(
    project_id: str,
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> ServicesListResponse:
    """List all services for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    services, total = store.list_services(
        service_type=service_type,
        project_id=project_id,
        page=page,
        limit=limit,
    )
    
    return ServicesListResponse(
        items=[ServiceResponse(**s.to_dict()) for s in services],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("/{project_id}/services", response_model=ServiceResponse)
async def create_project_service(project_id: str, request: ServiceCreate) -> ServiceResponse:
    """Create a new service for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if request.service_type not in VALID_SERVICE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service type. Must be one of: {', '.join(VALID_SERVICE_TYPES)}"
        )
    
    try:
        service = store.create_service(
            name=request.name,
            service_type=request.service_type,
            endpoint_url=request.endpoint_url,
            description=request.description,
            health_endpoint=request.health_endpoint,
            auth_type=request.auth_type,
            credentials_ref=request.credentials_ref,
            config_yaml=request.config_yaml,
            is_global=request.is_global,
            project_id=project_id if not request.is_global else None,
            tags=request.tags,
            metadata=request.metadata,
        )
        return ServiceResponse(**service.to_dict())
    except Exception as e:
        logger.error(f"Failed to create service: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/services/{service_id}", response_model=ServiceResponse)
async def get_project_service(project_id: str, service_id: str) -> ServiceResponse:
    """Get a service by ID."""
    store = _get_store()
    service = store.get_service(service_id)
    
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify service belongs to project or is global
    if service.project_id != project_id and not service.is_global:
        raise HTTPException(status_code=404, detail="Service not found in this project")
    
    return ServiceResponse(**service.to_dict())


@router.put("/{project_id}/services/{service_id}", response_model=ServiceResponse)
async def update_project_service(project_id: str, service_id: str, request: ServiceUpdate) -> ServiceResponse:
    """Update a service."""
    store = _get_store()
    service = store.get_service(service_id)
    
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.project_id != project_id and not service.is_global:
        raise HTTPException(status_code=404, detail="Service not found in this project")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    updated = store.update_service(service_id, **update_data)
    
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update service")
    
    return ServiceResponse(**updated.to_dict())


@router.delete("/{project_id}/services/{service_id}")
async def delete_project_service(project_id: str, service_id: str) -> dict:
    """Delete a service."""
    store = _get_store()
    service = store.get_service(service_id)
    
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.project_id != project_id and not service.is_global:
        raise HTTPException(status_code=404, detail="Service not found in this project")
    
    if not store.delete_service(service_id):
        raise HTTPException(status_code=500, detail="Failed to delete service")
    
    return {"status": "deleted", "id": service_id}


@router.post("/{project_id}/services/{service_id}/health")
async def check_service_health(project_id: str, service_id: str) -> dict:
    """Check health of a service."""
    store = _get_store()
    service = store.get_service(service_id)
    
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.project_id != project_id and not service.is_global:
        raise HTTPException(status_code=404, detail="Service not found in this project")
    
    # Perform health check
    status = "unknown"
    message = ""
    
    if service.health_endpoint:
        try:
            import httpx
            url = f"{service.endpoint_url.rstrip('/')}{service.health_endpoint}"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code < 400:
                    status = "healthy"
                    message = f"Status code: {response.status_code}"
                else:
                    status = "unhealthy"
                    message = f"Status code: {response.status_code}"
        except Exception as e:
            status = "unhealthy"
            message = str(e)
    else:
        message = "No health endpoint configured"
    
    # Update service status
    store.update_service(
        service_id,
        status=status,
        last_health_check=datetime.utcnow(),
    )
    
    return {
        "service_id": service_id,
        "status": status,
        "message": message,
        "checked_at": datetime.utcnow().isoformat(),
    }


# === Indexing State Endpoints ===

@router.get("/{project_id}/index", response_model=IndexingStateResponse)
async def get_indexing_state(project_id: str) -> IndexingStateResponse:
    """Get indexing state for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    state = store.get_or_create_indexing_state(project_id)
    return IndexingStateResponse(**state.to_dict())


@router.post("/{project_id}/index")
async def trigger_indexing(project_id: str, request: IndexRequest) -> dict:
    """Trigger codebase indexing for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update indexing state to "indexing"
    state = store.update_indexing_state(
        project_id,
        status="indexing",
        error_message=None,
    )
    
    # TODO: Trigger actual indexing in background
    # For now, return the current state
    return {
        "status": "indexing_started",
        "project_id": project_id,
        "force": request.force,
        "path": request.path,
        "state": state.to_dict() if state else None,
    }


@router.get("/{project_id}/index/status")
async def get_indexing_status(project_id: str) -> dict:
    """Get current indexing status for a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    state = store.get_or_create_indexing_state(project_id)
    
    return {
        "project_id": project_id,
        "status": state.status,
        "version": state.version,
        "file_count": state.file_count,
        "chunk_count": state.chunk_count,
        "last_indexed": state.last_indexed.isoformat() if state.last_indexed else None,
        "needs_reindex": state.version != "2.0",  # Check against current version
    }


# === Project Resources Endpoints ===

@router.post("/{project_id}/resources/link")
async def link_resource(
    project_id: str,
    resource_type: str = Query(..., description="Resource type (datasource, service)"),
    resource_id: str = Query(..., description="Resource ID to link"),
    alias: Optional[str] = Query(None, description="Optional alias"),
) -> dict:
    """Link a global resource to a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if resource_type not in ("datasource", "service"):
        raise HTTPException(status_code=400, detail="Invalid resource type")
    
    link = store.link_resource_to_project(
        project_id=project_id,
        resource_type=resource_type,
        resource_id=resource_id,
        alias=alias,
    )
    
    return {
        "status": "linked",
        "project_id": project_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "alias": alias,
        "link_id": link.id,
    }


@router.delete("/{project_id}/resources/unlink")
async def unlink_resource(
    project_id: str,
    resource_type: str = Query(..., description="Resource type"),
    resource_id: str = Query(..., description="Resource ID to unlink"),
) -> dict:
    """Unlink a resource from a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = store.unlink_resource_from_project(
        project_id=project_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Resource link not found")
    
    return {
        "status": "unlinked",
        "project_id": project_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
    }


@router.get("/{project_id}/resources")
async def list_project_resources(
    project_id: str,
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
) -> dict:
    """List all resources linked to a project."""
    store = _get_store()
    project = store.get_project(project_id)
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    resources = store.get_project_resources(project_id, resource_type)
    
    return {
        "project_id": project_id,
        "resources": [r.to_dict() for r in resources],
        "count": len(resources),
    }

