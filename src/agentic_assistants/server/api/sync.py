"""
REST API endpoints for data synchronization.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentic_assistants.sync import SyncManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncSessionRequest(BaseModel):
    """Request to start a sync session."""
    source_env: str
    target_env: str
    entity_types: Optional[List[str]] = None
    strategy: Optional[str] = "last-write-wins"


class SyncSessionResponse(BaseModel):
    """Response from sync session start."""
    session_id: str
    status: str
    message: str


class ConflictResolutionRequest(BaseModel):
    """Request to resolve a conflict."""
    resolution: str  # use_source, use_target, merge
    resolved_by: Optional[str] = None


@router.post("/sessions", response_model=SyncSessionResponse)
async def start_sync(request: SyncSessionRequest):
    """
    Start a data synchronization session.
    
    Args:
        request: Sync session request
        
    Returns:
        Sync session response
    """
    from agentic_assistants.sync.sync_manager import SyncStrategy
    
    sync_manager = SyncManager()
    
    try:
        strategy = SyncStrategy(request.strategy)
    except ValueError:
        raise HTTPException(400, f"Invalid strategy: {request.strategy}")
    
    session_id = sync_manager.start_sync(
        source_env=request.source_env,
        target_env=request.target_env,
        entity_types=request.entity_types,
        strategy=strategy,
    )
    
    return SyncSessionResponse(
        session_id=session_id,
        status="running",
        message="Sync session started",
    )


@router.get("/conflicts")
async def list_conflicts(
    session_id: Optional[str] = None,
    resolved: bool = False,
):
    """
    List sync conflicts.
    
    Args:
        session_id: Optional session ID filter
        resolved: Include resolved conflicts
        
    Returns:
        List of conflicts
    """
    sync_manager = SyncManager()
    conflicts = sync_manager.get_conflicts(
        session_id=session_id,
        resolved=resolved,
    )
    
    return {"conflicts": conflicts}


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: str,
    request: ConflictResolutionRequest,
):
    """
    Resolve a sync conflict.
    
    Args:
        conflict_id: Conflict ID
        request: Resolution request
        
    Returns:
        Success message
    """
    sync_manager = SyncManager()
    
    sync_manager.resolve_conflict(
        conflict_id=conflict_id,
        resolution=request.resolution,
        resolved_by=request.resolved_by,
    )
    
    return {
        "status": "resolved",
        "conflict_id": conflict_id,
        "resolution": request.resolution,
    }
