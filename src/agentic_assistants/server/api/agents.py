"""
Agents API Router.

This module provides REST endpoints for agent management.
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# === Request/Response Models ===

class AgentCreate(BaseModel):
    """Request to create a new agent."""
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role")
    goal: str = Field(default="", description="Agent goal")
    backstory: str = Field(default="", description="Agent backstory")
    tools: List[str] = Field(default_factory=list, description="Tools available to agent")
    model: str = Field(default="llama3.2", description="LLM model to use")
    status: str = Field(default="drafted", description="Agent status")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    config_yaml: str = Field(default="", description="Agent configuration in YAML")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class AgentUpdate(BaseModel):
    """Request to update an agent."""
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[List[str]] = None
    model: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[str] = None
    config_yaml: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    model: str
    status: str
    project_id: Optional[str]
    config_yaml: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class AgentsListResponse(BaseModel):
    """Response containing list of agents."""
    items: List[AgentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


# === Endpoints ===

@router.get("", response_model=AgentsListResponse)
async def list_agents(
    project_id: Optional[str] = Query(None, description="Filter by project"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> AgentsListResponse:
    """List all agents with optional filtering."""
    store = _get_store()
    agents, total = store.list_agents(
        project_id=project_id, status=status, page=page, limit=limit
    )
    
    return AgentsListResponse(
        items=[AgentResponse(**a.to_dict()) for a in agents],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("", response_model=AgentResponse)
async def create_agent(request: AgentCreate) -> AgentResponse:
    """Create a new agent."""
    store = _get_store()
    
    try:
        agent = store.create_agent(
            name=request.name,
            role=request.role,
            goal=request.goal,
            backstory=request.backstory,
            tools=request.tools,
            model=request.model,
            status=request.status,
            project_id=request.project_id,
            config_yaml=request.config_yaml,
            tags=request.tags,
            metadata=request.metadata,
        )
        return AgentResponse(**agent.to_dict())
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get an agent by ID."""
    store = _get_store()
    agent = store.get_agent(agent_id)
    
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(**agent.to_dict())


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, request: AgentUpdate) -> AgentResponse:
    """Update an agent."""
    store = _get_store()
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    agent = store.update_agent(agent_id, **update_data)
    
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(**agent.to_dict())


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str) -> dict:
    """Delete an agent."""
    store = _get_store()
    
    if not store.delete_agent(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"status": "deleted", "id": agent_id}


@router.post("/{agent_id}/deploy")
async def deploy_agent(agent_id: str) -> dict:
    """Deploy an agent (change status to deployed)."""
    store = _get_store()
    
    agent = store.update_agent(agent_id, status="deployed")
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"status": "deployed", "id": agent_id}


@router.post("/{agent_id}/run")
async def run_agent(agent_id: str, inputs: dict = None) -> dict:
    """Run an agent (placeholder for actual execution)."""
    store = _get_store()
    agent = store.get_agent(agent_id)
    
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # TODO: Implement actual agent execution
    return {
        "status": "running",
        "agent_id": agent_id,
        "message": "Agent execution not yet implemented",
    }

