"""
Tags API Router.

This module provides REST endpoints for tag management and resource tagging.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tags", tags=["tags"])


# === Request/Response Models ===

class TagCreate(BaseModel):
    """Request to create a new tag."""
    name: str = Field(..., description="Tag name")
    color: str = Field(default="#6366f1", description="Tag color (hex)")


class TagResponse(BaseModel):
    """Tag response model."""
    id: str
    name: str
    color: str
    resource_count: int


class TagResourceRequest(BaseModel):
    """Request to add a tag to a resource."""
    tag: str = Field(..., description="Tag name")


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


VALID_RESOURCE_TYPES = {"project", "agent", "flow", "component"}


# === Endpoints ===

@router.get("", response_model=List[TagResponse])
async def list_tags() -> List[TagResponse]:
    """List all tags with resource counts."""
    store = _get_store()
    tags = store.list_tags()
    return [TagResponse(**t.to_dict()) for t in tags]


@router.post("", response_model=TagResponse)
async def create_tag(request: TagCreate) -> TagResponse:
    """Create a new tag (or get existing one)."""
    store = _get_store()
    
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    
    # Validate hex color
    if not request.color.startswith("#") or len(request.color) != 7:
        raise HTTPException(
            status_code=400, 
            detail="Color must be a valid hex color (e.g., #6366f1)"
        )
    
    tag = store.get_or_create_tag(request.name.strip(), request.color)
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        resource_count=tag.resource_count,
    )


# Resource tagging endpoints

@router.post("/resources/{resource_type}/{resource_id}")
async def add_tag_to_resource(
    resource_type: str,
    resource_id: str,
    request: TagResourceRequest,
) -> dict:
    """Add a tag to a resource."""
    store = _get_store()
    
    if resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource type. Must be one of: {', '.join(VALID_RESOURCE_TYPES)}"
        )
    
    if not request.tag.strip():
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    
    success = store.add_tag_to_resource(resource_type, resource_id, request.tag.strip())
    
    if success:
        return {"status": "tagged", "resource_type": resource_type, "resource_id": resource_id, "tag": request.tag}
    else:
        return {"status": "already_tagged", "resource_type": resource_type, "resource_id": resource_id, "tag": request.tag}


@router.delete("/resources/{resource_type}/{resource_id}/{tag_name}")
async def remove_tag_from_resource(
    resource_type: str,
    resource_id: str,
    tag_name: str,
) -> dict:
    """Remove a tag from a resource."""
    store = _get_store()
    
    if resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource type. Must be one of: {', '.join(VALID_RESOURCE_TYPES)}"
        )
    
    success = store.remove_tag_from_resource(resource_type, resource_id, tag_name)
    
    if success:
        return {"status": "untagged", "resource_type": resource_type, "resource_id": resource_id, "tag": tag_name}
    else:
        raise HTTPException(status_code=404, detail="Tag not found on resource")

