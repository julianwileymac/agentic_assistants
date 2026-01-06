"""
Flows API Router.

This module provides REST endpoints for multi-agent flow management.
"""

from typing import Optional, List

import yaml
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/flows", tags=["flows"])


# === Request/Response Models ===

class FlowCreate(BaseModel):
    """Request to create a new flow."""
    name: str = Field(..., description="Flow name")
    description: str = Field(default="", description="Flow description")
    flow_yaml: str = Field(default="", description="Flow definition in YAML")
    flow_type: str = Field(default="crew", description="Flow type (crew, pipeline, workflow)")
    status: str = Field(default="draft", description="Flow status")
    agents: List[str] = Field(default_factory=list, description="Agent IDs in flow")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    tags: List[str] = Field(default_factory=list, description="Flow tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class FlowUpdate(BaseModel):
    """Request to update a flow."""
    name: Optional[str] = None
    description: Optional[str] = None
    flow_yaml: Optional[str] = None
    flow_type: Optional[str] = None
    status: Optional[str] = None
    agents: Optional[List[str]] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class FlowResponse(BaseModel):
    """Flow response model."""
    id: str
    name: str
    description: str
    flow_yaml: str
    flow_type: str
    status: str
    agents: List[str]
    project_id: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class FlowsListResponse(BaseModel):
    """Response containing list of flows."""
    items: List[FlowResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class FlowValidationResponse(BaseModel):
    """Response from flow validation."""
    valid: bool
    errors: List[str]
    warnings: List[str] = Field(default_factory=list)


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


def _validate_flow_yaml(flow_yaml: str) -> tuple[bool, List[str], List[str]]:
    """Validate flow YAML syntax and structure."""
    errors = []
    warnings = []
    
    if not flow_yaml.strip():
        return True, [], ["Flow YAML is empty"]
    
    try:
        flow_def = yaml.safe_load(flow_yaml)
        
        if not isinstance(flow_def, dict):
            errors.append("Flow definition must be a YAML object")
            return False, errors, warnings
        
        # Check required fields
        if "name" not in flow_def:
            warnings.append("Flow definition should include a 'name' field")
        
        if "agents" not in flow_def and "tasks" not in flow_def:
            warnings.append("Flow definition should include 'agents' or 'tasks'")
        
        # Validate agents if present
        if "agents" in flow_def:
            if not isinstance(flow_def["agents"], list):
                errors.append("'agents' must be a list")
            else:
                for i, agent in enumerate(flow_def["agents"]):
                    if not isinstance(agent, dict):
                        errors.append(f"Agent at index {i} must be an object")
                    elif "name" not in agent:
                        warnings.append(f"Agent at index {i} should have a 'name' field")
        
        # Validate tasks if present
        if "tasks" in flow_def:
            if not isinstance(flow_def["tasks"], list):
                errors.append("'tasks' must be a list")
            else:
                for i, task in enumerate(flow_def["tasks"]):
                    if not isinstance(task, dict):
                        errors.append(f"Task at index {i} must be an object")
                    elif "description" not in task:
                        warnings.append(f"Task at index {i} should have a 'description' field")
        
        return len(errors) == 0, errors, warnings
        
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {str(e)}")
        return False, errors, warnings


# === Endpoints ===

@router.get("", response_model=FlowsListResponse)
async def list_flows(
    project_id: Optional[str] = Query(None, description="Filter by project"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> FlowsListResponse:
    """List all flows with optional filtering."""
    store = _get_store()
    flows, total = store.list_flows(
        project_id=project_id, status=status, page=page, limit=limit
    )
    
    return FlowsListResponse(
        items=[FlowResponse(**f.to_dict()) for f in flows],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=FlowResponse)
async def create_flow(request: FlowCreate) -> FlowResponse:
    """Create a new flow."""
    store = _get_store()
    
    # Validate YAML if provided
    if request.flow_yaml:
        valid, errors, _ = _validate_flow_yaml(request.flow_yaml)
        if not valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid flow YAML: {'; '.join(errors)}"
            )
    
    try:
        flow = store.create_flow(
            name=request.name,
            description=request.description,
            flow_yaml=request.flow_yaml,
            flow_type=request.flow_type,
            status=request.status,
            agents=request.agents,
            project_id=request.project_id,
            tags=request.tags,
            metadata=request.metadata,
        )
        return FlowResponse(**flow.to_dict())
    except Exception as e:
        logger.error(f"Failed to create flow: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(flow_id: str) -> FlowResponse:
    """Get a flow by ID."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    return FlowResponse(**flow.to_dict())


@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(flow_id: str, request: FlowUpdate) -> FlowResponse:
    """Update a flow."""
    store = _get_store()
    
    # Validate YAML if being updated
    if request.flow_yaml:
        valid, errors, _ = _validate_flow_yaml(request.flow_yaml)
        if not valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid flow YAML: {'; '.join(errors)}"
            )
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    flow = store.update_flow(flow_id, **update_data)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    return FlowResponse(**flow.to_dict())


@router.delete("/{flow_id}")
async def delete_flow(flow_id: str) -> dict:
    """Delete a flow."""
    store = _get_store()
    
    if not store.delete_flow(flow_id):
        raise HTTPException(status_code=404, detail="Flow not found")
    
    return {"status": "deleted", "id": flow_id}


@router.get("/{flow_id}/validate", response_model=FlowValidationResponse)
async def validate_flow(flow_id: str) -> FlowValidationResponse:
    """Validate a flow's YAML definition."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    valid, errors, warnings = _validate_flow_yaml(flow.flow_yaml)
    
    return FlowValidationResponse(
        valid=valid,
        errors=errors,
        warnings=warnings,
    )


@router.post("/{flow_id}/run")
async def run_flow(flow_id: str, inputs: dict = None) -> dict:
    """Run a flow (placeholder for actual execution)."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # TODO: Implement actual flow execution using CrewAI
    return {
        "status": "running",
        "flow_id": flow_id,
        "message": "Flow execution not yet implemented",
    }

