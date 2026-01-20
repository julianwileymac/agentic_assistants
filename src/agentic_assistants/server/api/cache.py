"""
Cache API Router.

This module provides REST endpoints for cache operations,
including solution caching and workflow state management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/cache", tags=["cache"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SolutionRequest(BaseModel):
    """Request to store a solution."""
    name: str = Field(..., description="Solution name")
    description: str = Field(default="", description="Solution description")
    solution_type: str = Field(default="code", description="Solution type")
    content: Any = Field(default=None, description="Solution content")
    code: str = Field(default="", description="Code content")
    tags: List[str] = Field(default_factory=list, description="Tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    is_global: bool = Field(default=False, description="Global solution")


class SolutionResponse(BaseModel):
    """Response with a solution."""
    id: str
    name: str
    description: str
    solution_type: str
    content: Any = None
    code: str = ""
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    use_count: int = 0
    success_rate: float = 1.0
    created_at: str
    updated_at: str
    project_id: Optional[str] = None
    is_global: bool = False


class WorkflowStateResponse(BaseModel):
    """Response with workflow state."""
    workflow_id: str
    name: str
    status: str
    current_step: int
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: str
    updated_at: str


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow."""
    name: str = Field(..., description="Workflow name")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    context: Dict[str, Any] = Field(default_factory=dict, description="Initial context")
    user_id: Optional[str] = Field(default=None, description="User ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    project_id: Optional[str] = Field(default=None, description="Project ID")


class UpdateWorkflowStepRequest(BaseModel):
    """Request to update a workflow step."""
    step_index: int = Field(..., description="Step index")
    result: Any = Field(..., description="Step result")
    status: str = Field(default="running", description="Workflow status")


class CacheStatsResponse(BaseModel):
    """Response with cache statistics."""
    total_solutions: int = 0
    total_tags: int = 0
    active_workflows: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    cache_info: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Helper Functions
# ============================================================================

def _get_solution_cache():
    """Get solution cache instance."""
    from agentic_assistants.cache import get_solution_cache
    return get_solution_cache()


def _solution_to_response(solution) -> SolutionResponse:
    """Convert Solution to response model."""
    return SolutionResponse(
        id=solution.id,
        name=solution.name,
        description=solution.description,
        solution_type=solution.solution_type.value if hasattr(solution.solution_type, 'value') else str(solution.solution_type),
        content=solution.content,
        code=solution.code,
        tags=solution.tags,
        metadata=solution.metadata,
        use_count=solution.use_count,
        success_rate=solution.success_rate,
        created_at=solution.created_at.isoformat() if hasattr(solution.created_at, 'isoformat') else str(solution.created_at),
        updated_at=solution.updated_at.isoformat() if hasattr(solution.updated_at, 'isoformat') else str(solution.updated_at),
        project_id=solution.project_id,
        is_global=solution.is_global,
    )


def _workflow_to_response(state) -> WorkflowStateResponse:
    """Convert WorkflowState to response model."""
    return WorkflowStateResponse(
        workflow_id=state.workflow_id,
        name=state.name,
        status=state.status,
        current_step=state.current_step,
        steps=state.steps,
        results=state.results,
        context=state.context,
        error=state.error,
        created_at=state.created_at.isoformat() if hasattr(state.created_at, 'isoformat') else str(state.created_at),
        updated_at=state.updated_at.isoformat() if hasattr(state.updated_at, 'isoformat') else str(state.updated_at),
    )


# ============================================================================
# Solution Endpoints
# ============================================================================

@router.post("/solutions", response_model=SolutionResponse)
async def store_solution(request: SolutionRequest) -> SolutionResponse:
    """Store a solution in the cache."""
    try:
        from agentic_assistants.cache.solution_store import Solution, SolutionType
        
        cache = _get_solution_cache()
        
        # Parse solution type
        try:
            sol_type = SolutionType(request.solution_type)
        except ValueError:
            sol_type = SolutionType.CODE
        
        solution = Solution(
            name=request.name,
            description=request.description,
            solution_type=sol_type,
            content=request.content,
            code=request.code,
            tags=request.tags,
            metadata=request.metadata,
            project_id=request.project_id,
            is_global=request.is_global,
        )
        
        cache.store(solution)
        
        return _solution_to_response(solution)
        
    except Exception as e:
        logger.error(f"Error storing solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/solutions/{name}", response_model=SolutionResponse)
async def get_solution(
    name: str,
    project_id: Optional[str] = Query(None, description="Project ID"),
) -> SolutionResponse:
    """Get a solution by name."""
    try:
        cache = _get_solution_cache()
        solution = cache.get(name, project_id)
        
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
        
        return _solution_to_response(solution)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/solutions/{name}")
async def delete_solution(
    name: str,
    project_id: Optional[str] = Query(None, description="Project ID"),
) -> Dict[str, Any]:
    """Delete a solution."""
    try:
        cache = _get_solution_cache()
        success = cache.delete(name, project_id)
        
        return {
            "success": success,
            "name": name,
        }
        
    except Exception as e:
        logger.error(f"Error deleting solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/solutions", response_model=List[SolutionResponse])
async def list_solutions(
    project_id: Optional[str] = Query(None, description="Project ID filter"),
    include_global: bool = Query(True, description="Include global solutions"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
) -> List[SolutionResponse]:
    """List all solutions."""
    try:
        cache = _get_solution_cache()
        solutions = cache.list_all(
            project_id=project_id,
            include_global=include_global,
            limit=limit,
        )
        
        return [_solution_to_response(s) for s in solutions]
        
    except Exception as e:
        logger.error(f"Error listing solutions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/solutions/search/tags", response_model=List[SolutionResponse])
async def search_solutions_by_tags(
    tags: List[str] = Query(..., description="Tags to search for"),
    operator: str = Query("AND", description="AND or OR"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
) -> List[SolutionResponse]:
    """Search solutions by tags."""
    try:
        cache = _get_solution_cache()
        solutions = cache.search_by_tags(
            tags=tags,
            operator=operator,
            limit=limit,
        )
        
        return [_solution_to_response(s) for s in solutions]
        
    except Exception as e:
        logger.error(f"Error searching solutions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/solutions/search", response_model=List[SolutionResponse])
async def search_solutions(
    query: str = Query(..., description="Search query"),
    solution_type: Optional[str] = Query(None, description="Solution type filter"),
    project_id: Optional[str] = Query(None, description="Project ID filter"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> List[SolutionResponse]:
    """Search solutions by text."""
    try:
        from agentic_assistants.cache.solution_store import SolutionType
        
        cache = _get_solution_cache()
        
        sol_type = None
        if solution_type:
            try:
                sol_type = SolutionType(solution_type)
            except ValueError:
                pass
        
        solutions = cache.search(
            query=query,
            solution_type=sol_type,
            project_id=project_id,
            limit=limit,
        )
        
        return [_solution_to_response(s) for s in solutions]
        
    except Exception as e:
        logger.error(f"Error searching solutions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/solutions/{name}/success")
async def record_solution_success(
    name: str,
    success: bool = Query(..., description="Whether usage was successful"),
    project_id: Optional[str] = Query(None, description="Project ID"),
) -> Dict[str, Any]:
    """Record success/failure for a solution usage."""
    try:
        cache = _get_solution_cache()
        cache.record_success(name, success, project_id)
        
        return {
            "success": True,
            "name": name,
            "recorded_success": success,
        }
        
    except Exception as e:
        logger.error(f"Error recording solution success: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_all_tags() -> Dict[str, Any]:
    """Get all tags in use."""
    try:
        cache = _get_solution_cache()
        tags = cache.get_tags()
        
        return {
            "tags": tags,
            "count": len(tags),
        }
        
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Workflow Endpoints
# ============================================================================

@router.post("/workflows", response_model=WorkflowStateResponse)
async def create_workflow(request: CreateWorkflowRequest) -> WorkflowStateResponse:
    """Create a new workflow."""
    try:
        from agentic_assistants.cache.solution_store import WorkflowState
        
        cache = _get_solution_cache()
        
        state = WorkflowState(
            name=request.name,
            status="pending",
            steps=request.steps,
            context=request.context,
            user_id=request.user_id,
            session_id=request.session_id,
            project_id=request.project_id,
        )
        
        cache.save_workflow_state(state)
        
        return _workflow_to_response(state)
        
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowStateResponse)
async def get_workflow(workflow_id: str) -> WorkflowStateResponse:
    """Get workflow state."""
    try:
        cache = _get_solution_cache()
        state = cache.get_workflow_state(workflow_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return _workflow_to_response(state)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workflows/{workflow_id}/step", response_model=WorkflowStateResponse)
async def update_workflow_step(
    workflow_id: str,
    request: UpdateWorkflowStepRequest,
) -> WorkflowStateResponse:
    """Update workflow step progress."""
    try:
        cache = _get_solution_cache()
        state = cache.update_workflow_step(
            workflow_id=workflow_id,
            step_index=request.step_index,
            result=request.result,
            status=request.status,
        )
        
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return _workflow_to_response(state)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/fail")
async def fail_workflow(
    workflow_id: str,
    error: str = Query(..., description="Error message"),
) -> WorkflowStateResponse:
    """Mark workflow as failed."""
    try:
        cache = _get_solution_cache()
        state = cache.fail_workflow(workflow_id, error)
        
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return _workflow_to_response(state)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error failing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows", response_model=List[WorkflowStateResponse])
async def list_active_workflows(
    user_id: Optional[str] = Query(None, description="User ID filter"),
    session_id: Optional[str] = Query(None, description="Session ID filter"),
) -> List[WorkflowStateResponse]:
    """List active workflows."""
    try:
        cache = _get_solution_cache()
        workflows = cache.list_active_workflows(
            user_id=user_id,
            session_id=session_id,
        )
        
        return [_workflow_to_response(w) for w in workflows]
        
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Stats Endpoints
# ============================================================================

@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats() -> CacheStatsResponse:
    """Get cache statistics."""
    try:
        cache = _get_solution_cache()
        stats = cache.get_stats()
        
        return CacheStatsResponse(
            total_solutions=stats.get("total_solutions", 0),
            total_tags=stats.get("total_tags", 0),
            active_workflows=stats.get("active_workflows", 0),
            by_type=stats.get("by_type", {}),
            cache_info=stats.get("cache_info", {}),
        )
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_cache(
    prefix: Optional[str] = Query(None, description="Key prefix to clear"),
) -> Dict[str, Any]:
    """Clear cache entries."""
    try:
        from agentic_assistants.cache import get_cache
        
        cache = get_cache()
        
        if prefix:
            count = cache.clear_namespace(prefix)
        else:
            count = cache.clear_all()
        
        return {
            "success": True,
            "keys_cleared": count,
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
