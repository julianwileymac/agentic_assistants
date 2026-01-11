"""
Pipeline API endpoints.

This module provides REST API endpoints for managing and executing
pipelines in the Agentic framework.

Endpoints:
- GET /pipelines - List all registered pipelines
- GET /pipelines/{name} - Get pipeline details
- POST /pipelines/{name}/run - Execute a pipeline
- GET /pipelines/{name}/status - Get pipeline run status
- GET /pipelines/{name}/visualize - Get pipeline visualization data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class NodeInfo(BaseModel):
    """Information about a pipeline node."""
    name: str
    inputs: List[str]
    outputs: List[str]
    tags: List[str] = []


class PipelineInfo(BaseModel):
    """Information about a pipeline."""
    name: str
    node_count: int
    inputs: List[str]
    outputs: List[str]
    nodes: List[NodeInfo]


class PipelineListResponse(BaseModel):
    """Response for pipeline list endpoint."""
    pipelines: List[str]
    count: int


class PipelineRunRequest(BaseModel):
    """Request to run a pipeline."""
    runner: str = Field(default="sequential", description="Runner type: sequential, parallel, thread")
    from_nodes: Optional[List[str]] = Field(default=None, description="Start from these nodes")
    to_nodes: Optional[List[str]] = Field(default=None, description="Run up to these nodes")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    async_run: bool = Field(default=False, description="Run asynchronously")


class NodeRunInfo(BaseModel):
    """Information about a node execution."""
    node_name: str
    success: bool
    duration_seconds: float
    error: Optional[str] = None


class PipelineRunResponse(BaseModel):
    """Response from a pipeline run."""
    run_id: str
    pipeline_name: str
    success: bool
    duration_seconds: float
    node_count: int
    nodes_executed: int
    errors: List[str] = []
    status: str = "completed"  # pending, running, completed, failed


class PipelineRunStatus(BaseModel):
    """Status of a pipeline run."""
    run_id: str
    pipeline_name: str
    status: str
    progress: float
    nodes_completed: int
    nodes_total: int
    errors: List[str] = []
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class PipelineVisualization(BaseModel):
    """Pipeline visualization data."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


# ============================================================================
# In-memory run tracking (would use a proper store in production)
# ============================================================================

_pipeline_runs: Dict[str, PipelineRunStatus] = {}


def _get_registry():
    """Get the pipeline registry."""
    from agentic_assistants.pipelines.registry import get_pipeline_registry
    return get_pipeline_registry()


def _get_catalog():
    """Get the data catalog."""
    from agentic_assistants.data.catalog import DataCatalog
    return DataCatalog()


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=PipelineListResponse)
async def list_pipelines():
    """
    List all registered pipelines.
    
    Returns:
        List of pipeline names
    """
    registry = _get_registry()
    pipelines = registry.list_pipelines()
    
    return PipelineListResponse(
        pipelines=pipelines,
        count=len(pipelines),
    )


@router.get("/{name}", response_model=PipelineInfo)
async def get_pipeline(name: str):
    """
    Get details about a specific pipeline.
    
    Args:
        name: Pipeline name
        
    Returns:
        Pipeline information including nodes
    """
    registry = _get_registry()
    
    if name == "__default__":
        pipeline = registry.get_default_pipeline()
    else:
        pipeline = registry.get(name)
    
    if pipeline is None:
        raise HTTPException(status_code=404, detail=f"Pipeline '{name}' not found")
    
    nodes = [
        NodeInfo(
            name=node.name,
            inputs=node.input_names,
            outputs=node.output_names,
            tags=list(node.tags),
        )
        for node in pipeline.topological_sort()
    ]
    
    return PipelineInfo(
        name=name,
        node_count=len(pipeline),
        inputs=list(pipeline.inputs),
        outputs=list(pipeline.outputs),
        nodes=nodes,
    )


@router.post("/{name}/run", response_model=PipelineRunResponse)
async def run_pipeline(
    name: str,
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Execute a pipeline.
    
    Args:
        name: Pipeline name
        request: Run configuration
        
    Returns:
        Run result or status for async runs
    """
    registry = _get_registry()
    catalog = _get_catalog()
    
    # Get pipeline
    if name == "__default__":
        pipeline = registry.get_default_pipeline()
    else:
        pipeline = registry.get(name)
    
    if pipeline is None:
        raise HTTPException(status_code=404, detail=f"Pipeline '{name}' not found")
    
    # Apply filters
    if request.from_nodes:
        pipeline = pipeline.from_nodes(*request.from_nodes)
    if request.to_nodes:
        pipeline = pipeline.to_nodes(*request.to_nodes)
    if request.tags:
        pipeline = pipeline.only_nodes_with_tags(*request.tags)
    
    # Generate run ID
    run_id = str(uuid4())
    
    if request.async_run:
        # Track run status
        _pipeline_runs[run_id] = PipelineRunStatus(
            run_id=run_id,
            pipeline_name=name,
            status="pending",
            progress=0.0,
            nodes_completed=0,
            nodes_total=len(pipeline),
            started_at=datetime.utcnow().isoformat(),
        )
        
        # Run in background
        background_tasks.add_task(
            _run_pipeline_async,
            run_id,
            name,
            pipeline,
            catalog,
            request.runner,
        )
        
        return PipelineRunResponse(
            run_id=run_id,
            pipeline_name=name,
            success=True,
            duration_seconds=0.0,
            node_count=len(pipeline),
            nodes_executed=0,
            status="pending",
        )
    else:
        # Run synchronously
        result = _execute_pipeline(pipeline, catalog, request.runner, run_id)
        
        return PipelineRunResponse(
            run_id=run_id,
            pipeline_name=name,
            success=result.success,
            duration_seconds=result.duration_seconds,
            node_count=len(pipeline),
            nodes_executed=len(result.node_results),
            errors=result.errors,
            status="completed" if result.success else "failed",
        )


def _execute_pipeline(pipeline, catalog, runner_type: str, run_id: str):
    """Execute a pipeline with the specified runner."""
    from agentic_assistants.pipelines.runners import (
        SequentialRunner,
        ParallelRunner,
        ThreadRunner,
    )
    
    if runner_type == "parallel":
        runner = ParallelRunner()
    elif runner_type == "thread":
        runner = ThreadRunner()
    else:
        runner = SequentialRunner()
    
    return runner.run(pipeline, catalog, run_id=run_id)


async def _run_pipeline_async(
    run_id: str,
    name: str,
    pipeline,
    catalog,
    runner_type: str,
):
    """Run a pipeline asynchronously and update status."""
    try:
        _pipeline_runs[run_id].status = "running"
        
        result = _execute_pipeline(pipeline, catalog, runner_type, run_id)
        
        _pipeline_runs[run_id].status = "completed" if result.success else "failed"
        _pipeline_runs[run_id].progress = 1.0
        _pipeline_runs[run_id].nodes_completed = len(result.node_results)
        _pipeline_runs[run_id].completed_at = datetime.utcnow().isoformat()
        _pipeline_runs[run_id].errors = result.errors
        
    except Exception as e:
        _pipeline_runs[run_id].status = "failed"
        _pipeline_runs[run_id].errors = [str(e)]
        _pipeline_runs[run_id].completed_at = datetime.utcnow().isoformat()


@router.get("/{name}/status/{run_id}", response_model=PipelineRunStatus)
async def get_pipeline_status(name: str, run_id: str):
    """
    Get the status of a pipeline run.
    
    Args:
        name: Pipeline name
        run_id: Run identifier
        
    Returns:
        Current run status
    """
    if run_id not in _pipeline_runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    
    return _pipeline_runs[run_id]


@router.get("/{name}/visualize", response_model=PipelineVisualization)
async def visualize_pipeline(name: str):
    """
    Get visualization data for a pipeline.
    
    Returns nodes and edges for rendering a DAG visualization.
    
    Args:
        name: Pipeline name
        
    Returns:
        Nodes and edges for visualization
    """
    registry = _get_registry()
    
    if name == "__default__":
        pipeline = registry.get_default_pipeline()
    else:
        pipeline = registry.get(name)
    
    if pipeline is None:
        raise HTTPException(status_code=404, detail=f"Pipeline '{name}' not found")
    
    nodes = []
    edges = []
    
    # Track node positions for layout
    sorted_nodes = pipeline.topological_sort()
    
    # Add input nodes
    for i, input_name in enumerate(sorted(pipeline.inputs)):
        nodes.append({
            "id": input_name,
            "type": "input",
            "label": input_name,
            "position": {"x": 0, "y": i * 100},
        })
    
    # Add processing nodes
    for i, node in enumerate(sorted_nodes):
        nodes.append({
            "id": node.name,
            "type": "process",
            "label": node.name,
            "tags": list(node.tags),
            "position": {"x": 200, "y": i * 100},
        })
        
        # Add edges for inputs
        for input_name in node.input_names:
            edges.append({
                "id": f"{input_name}-{node.name}",
                "source": input_name,
                "target": node.name,
            })
        
        # Add output nodes and edges
        for output_name in node.output_names:
            if output_name in pipeline.outputs:
                # Final output
                nodes.append({
                    "id": output_name,
                    "type": "output",
                    "label": output_name,
                    "position": {"x": 400, "y": 0},
                })
            edges.append({
                "id": f"{node.name}-{output_name}",
                "source": node.name,
                "target": output_name,
            })
    
    return PipelineVisualization(nodes=nodes, edges=edges)


@router.delete("/{name}/runs/{run_id}")
async def delete_run(name: str, run_id: str):
    """Delete a pipeline run record."""
    if run_id not in _pipeline_runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    
    del _pipeline_runs[run_id]
    return {"status": "deleted", "run_id": run_id}


@router.get("/runs", response_model=List[PipelineRunStatus])
async def list_runs():
    """List all pipeline run statuses."""
    return list(_pipeline_runs.values())
