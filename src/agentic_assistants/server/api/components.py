"""
Components API Router.

This module provides REST endpoints for code component management.
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/components", tags=["components"])


# === Request/Response Models ===

class ComponentCreate(BaseModel):
    """Request to create a new component."""
    name: str = Field(..., description="Component name")
    category: str = Field(..., description="Component category (tool, agent, task, pattern, utility, template)")
    code: str = Field(default="", description="Component source code")
    language: str = Field(default="python", description="Programming language")
    description: str = Field(default="", description="Component description")
    usage_example: str = Field(default="", description="Usage example")
    version: str = Field(default="1.0.0", description="Component version")
    tags: List[str] = Field(default_factory=list, description="Component tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ComponentUpdate(BaseModel):
    """Request to update a component."""
    name: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    usage_example: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ComponentResponse(BaseModel):
    """Component response model."""
    id: str
    name: str
    category: str
    code: str
    language: str
    description: str
    usage_example: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class ComponentsListResponse(BaseModel):
    """Response containing list of components."""
    items: List[ComponentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


VALID_CATEGORIES = {"tool", "agent", "task", "pattern", "utility", "template"}


# === Endpoints ===

@router.get("", response_model=ComponentsListResponse)
async def list_components(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> ComponentsListResponse:
    """List all components with optional filtering."""
    store = _get_store()
    
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    components, total = store.list_components(
        category=category, search=search, page=page, limit=limit
    )
    
    return ComponentsListResponse(
        items=[ComponentResponse(**c.to_dict()) for c in components],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=ComponentResponse)
async def create_component(request: ComponentCreate) -> ComponentResponse:
    """Create a new component."""
    store = _get_store()
    
    if request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    try:
        component = store.create_component(
            name=request.name,
            category=request.category,
            code=request.code,
            language=request.language,
            description=request.description,
            usage_example=request.usage_example,
            version=request.version,
            tags=request.tags,
            metadata=request.metadata,
        )
        return ComponentResponse(**component.to_dict())
    except Exception as e:
        logger.error(f"Failed to create component: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: str) -> ComponentResponse:
    """Get a component by ID."""
    store = _get_store()
    component = store.get_component(component_id)
    
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return ComponentResponse(**component.to_dict())


@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(component_id: str, request: ComponentUpdate) -> ComponentResponse:
    """Update a component."""
    store = _get_store()
    
    if request.category and request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    component = store.update_component(component_id, **update_data)
    
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return ComponentResponse(**component.to_dict())


@router.delete("/{component_id}")
async def delete_component(component_id: str) -> dict:
    """Delete a component."""
    store = _get_store()
    
    if not store.delete_component(component_id):
        raise HTTPException(status_code=404, detail="Component not found")
    
    return {"status": "deleted", "id": component_id}


@router.get("/categories/list")
async def list_categories() -> dict:
    """List all valid component categories."""
    return {
        "categories": [
            {"id": "tool", "name": "Tool", "description": "Reusable agent tools"},
            {"id": "agent", "name": "Agent", "description": "Agent templates"},
            {"id": "task", "name": "Task", "description": "Task definitions"},
            {"id": "pattern", "name": "Pattern", "description": "Agentic patterns (RAG, ReAct, etc.)"},
            {"id": "utility", "name": "Utility", "description": "Utility functions"},
            {"id": "template", "name": "Template", "description": "Project templates"},
        ]
    }

