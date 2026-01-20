"""
Memory API Router.

This module provides REST endpoints for agent memory operations,
including mem0-backed memory storage and episodic memories.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AddMemoryRequest(BaseModel):
    """Request to add a memory."""
    content: str = Field(..., description="Memory content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    memory_type: str = Field(default="factual", description="Memory type (factual, episodic, preference)")
    user_id: Optional[str] = Field(default=None, description="User ID for scoping")
    session_id: Optional[str] = Field(default=None, description="Session ID for scoping")
    agent_id: Optional[str] = Field(default=None, description="Agent ID for scoping")


class MemoryResponse(BaseModel):
    """Response with a memory record."""
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    memory_type: str
    scope: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: str
    score: float = 0.0


class SearchMemoriesRequest(BaseModel):
    """Request to search memories."""
    query: str = Field(..., description="Search query")
    user_id: Optional[str] = Field(default=None, description="User ID filter")
    session_id: Optional[str] = Field(default=None, description="Session ID filter")
    memory_types: Optional[List[str]] = Field(default=None, description="Memory types to search")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")


class SearchMemoriesResponse(BaseModel):
    """Response with search results."""
    memories: List[MemoryResponse]
    total: int
    query: str
    search_time_ms: float


class ContextRequest(BaseModel):
    """Request to get context for a query."""
    query: str = Field(..., description="Query to get context for")
    user_id: Optional[str] = Field(default=None, description="User ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    max_memories: int = Field(default=5, ge=1, le=20, description="Maximum memories to include")
    max_length: int = Field(default=4000, description="Maximum context length")


class AddInteractionRequest(BaseModel):
    """Request to add an interaction as memory."""
    user_message: str = Field(..., description="User's message")
    assistant_response: str = Field(..., description="Assistant's response")
    user_id: Optional[str] = Field(default=None, description="User ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MemoryStatsResponse(BaseModel):
    """Response with memory store statistics."""
    user_id: Optional[str]
    session_id: Optional[str]
    backend: str
    total_memories: int = -1
    config: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Helper Functions
# ============================================================================

def _get_memory_store(user_id: Optional[str] = None, session_id: Optional[str] = None):
    """Get memory store instance."""
    from agentic_assistants.memory import get_memory_store
    return get_memory_store(
        backend="mem0",
        user_id=user_id,
        session_id=session_id,
    )


def _memory_to_response(memory) -> MemoryResponse:
    """Convert Memory to response model."""
    return MemoryResponse(
        id=memory.id,
        content=memory.content,
        metadata=memory.metadata,
        memory_type=memory.memory_type.value if hasattr(memory.memory_type, 'value') else str(memory.memory_type),
        scope=memory.scope.value if hasattr(memory.scope, 'value') else str(memory.scope),
        user_id=memory.user_id,
        session_id=memory.session_id,
        created_at=memory.created_at.isoformat() if hasattr(memory.created_at, 'isoformat') else str(memory.created_at),
        score=memory.score,
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/add", response_model=MemoryResponse)
async def add_memory(request: AddMemoryRequest) -> MemoryResponse:
    """Add a new memory."""
    try:
        from agentic_assistants.memory.base import MemoryType, MemoryScope
        
        store = _get_memory_store(request.user_id, request.session_id)
        
        # Parse memory type
        try:
            mem_type = MemoryType(request.memory_type)
        except ValueError:
            mem_type = MemoryType.FACTUAL
        
        memory = store.add_memory(
            content=request.content,
            metadata=request.metadata,
            memory_type=mem_type,
        )
        
        return _memory_to_response(memory)
        
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchMemoriesResponse)
async def search_memories(request: SearchMemoriesRequest) -> SearchMemoriesResponse:
    """Search memories by semantic similarity."""
    try:
        from agentic_assistants.memory.base import MemoryType
        
        store = _get_memory_store(request.user_id, request.session_id)
        
        # Parse memory types
        memory_types = None
        if request.memory_types:
            memory_types = []
            for mt in request.memory_types:
                try:
                    memory_types.append(MemoryType(mt))
                except ValueError:
                    pass
        
        result = store.search_memories(
            query=request.query,
            limit=request.limit,
            memory_types=memory_types,
        )
        
        return SearchMemoriesResponse(
            memories=[_memory_to_response(m) for m in result.memories],
            total=result.total,
            query=result.query,
            search_time_ms=result.search_time_ms,
        )
        
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context")
async def get_context(
    query: str = Query(..., description="Query to get context for"),
    user_id: Optional[str] = Query(None, description="User ID"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    max_memories: int = Query(5, ge=1, le=20, description="Maximum memories"),
    max_length: int = Query(4000, description="Maximum context length"),
) -> Dict[str, Any]:
    """Get relevant context for a query."""
    try:
        store = _get_memory_store(user_id, session_id)
        
        context = store.get_relevant_context(
            query=query,
            max_memories=max_memories,
            max_length=max_length,
        )
        
        return {
            "query": query,
            "context": context,
            "context_length": len(context),
        }
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction", response_model=MemoryResponse)
async def add_interaction(request: AddInteractionRequest) -> MemoryResponse:
    """Add an interaction (conversation turn) as episodic memory."""
    try:
        store = _get_memory_store(request.user_id, request.session_id)
        
        memory = store.add_interaction(
            user_message=request.user_message,
            assistant_response=request.assistant_response,
            metadata=request.metadata,
        )
        
        return _memory_to_response(memory)
        
    except Exception as e:
        logger.error(f"Error adding interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    user_id: Optional[str] = Query(None, description="User ID"),
    session_id: Optional[str] = Query(None, description="Session ID"),
) -> MemoryResponse:
    """Get a specific memory by ID."""
    try:
        store = _get_memory_store(user_id, session_id)
        memory = store.get_memory(memory_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return _memory_to_response(memory)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: Optional[str] = Query(None, description="User ID"),
    session_id: Optional[str] = Query(None, description="Session ID"),
) -> Dict[str, Any]:
    """Delete a memory."""
    try:
        store = _get_memory_store(user_id, session_id)
        success = store.delete_memory(memory_id)
        
        return {
            "success": success,
            "memory_id": memory_id,
        }
        
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_memories(
    user_id: Optional[str] = Query(None, description="User ID"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    memory_types: Optional[List[str]] = Query(None, description="Memory types to clear"),
) -> Dict[str, Any]:
    """Clear memories for a user/session."""
    try:
        from agentic_assistants.memory.base import MemoryType
        
        store = _get_memory_store(user_id, session_id)
        
        # Parse memory types
        types = None
        if memory_types:
            types = []
            for mt in memory_types:
                try:
                    types.append(MemoryType(mt))
                except ValueError:
                    pass
        
        count = store.clear_memories(memory_types=types)
        
        return {
            "success": True,
            "memories_cleared": count,
        }
        
    except Exception as e:
        logger.error(f"Error clearing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    user_id: Optional[str] = Query(None, description="User ID"),
    session_id: Optional[str] = Query(None, description="Session ID"),
) -> MemoryStatsResponse:
    """Get memory store statistics."""
    try:
        store = _get_memory_store(user_id, session_id)
        stats = store.get_stats()
        
        return MemoryStatsResponse(
            user_id=stats.get("user_id"),
            session_id=stats.get("session_id"),
            backend=stats.get("backend", "unknown"),
            total_memories=stats.get("total_memories", -1),
            config=stats.get("config", {}),
        )
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
