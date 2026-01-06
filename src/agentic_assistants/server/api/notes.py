"""
Notes API Router.

This module provides REST endpoints for free-form notes management.
Notes can be attached to any resource type (project, agent, flow, component, experiment).
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notes", tags=["notes"])


# === Request/Response Models ===

class NoteCreate(BaseModel):
    """Request to create a new note."""
    resource_type: str = Field(..., description="Resource type (project, agent, flow, component, experiment)")
    resource_id: str = Field(..., description="ID of the resource")
    content: str = Field(..., description="Note content (supports markdown)")


class NoteUpdate(BaseModel):
    """Request to update a note."""
    content: str = Field(..., description="Updated note content")


class NoteResponse(BaseModel):
    """Note response model."""
    id: str
    resource_type: str
    resource_id: str
    content: str
    created_at: str
    updated_at: str


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


VALID_RESOURCE_TYPES = {"project", "agent", "flow", "component", "experiment"}


# === Endpoints ===

@router.get("")
async def list_notes(
    resource_type: str = Query(..., description="Resource type"),
    resource_id: str = Query(..., description="Resource ID"),
) -> List[NoteResponse]:
    """List notes for a specific resource."""
    store = _get_store()
    
    if resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource type. Must be one of: {', '.join(VALID_RESOURCE_TYPES)}"
        )
    
    notes = store.get_notes(resource_type, resource_id)
    return [NoteResponse(**n.to_dict()) for n in notes]


@router.post("", response_model=NoteResponse)
async def create_note(request: NoteCreate) -> NoteResponse:
    """Create a new note attached to a resource."""
    store = _get_store()
    
    if request.resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource type. Must be one of: {', '.join(VALID_RESOURCE_TYPES)}"
        )
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    try:
        note = store.create_note(
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            content=request.content,
        )
        return NoteResponse(**note.to_dict())
    except Exception as e:
        logger.error(f"Failed to create note: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, request: NoteUpdate) -> NoteResponse:
    """Update a note."""
    store = _get_store()
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")
    
    note = store.update_note(note_id, request.content)
    
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(**note.to_dict())


@router.delete("/{note_id}")
async def delete_note(note_id: str) -> dict:
    """Delete a note."""
    store = _get_store()
    
    if not store.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"status": "deleted", "id": note_id}

