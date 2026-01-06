"""
Projects API Router.

This module provides REST endpoints for project management.
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
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

