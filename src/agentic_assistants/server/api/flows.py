"""
Flows API Router.

This module provides REST endpoints for multi-agent flow management,
including flow execution, node management, and observability.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, Optional, List

import yaml
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/flows", tags=["flows"])

# In-memory store for flow executions (would use database in production)
_flow_executions: Dict[str, Dict[str, Any]] = {}


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


class FlowNodeCreate(BaseModel):
    """Request to add a node to a flow."""
    type: str = Field(..., description="Node type (e.g., llmNode, retrieverNode)")
    label: str = Field(..., description="Node display label")
    position: Dict[str, float] = Field(..., description="Node position {x, y}")
    config: Dict[str, Any] = Field(default_factory=dict, description="Node configuration")
    description: Optional[str] = None


class FlowNodeUpdate(BaseModel):
    """Request to update a node."""
    label: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class FlowNodeResponse(BaseModel):
    """Flow node response."""
    id: str
    type: str
    label: str
    position: Dict[str, float]
    config: Dict[str, Any]
    description: Optional[str] = None


class FlowEdgeCreate(BaseModel):
    """Request to add an edge between nodes."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None


class FlowEdgeResponse(BaseModel):
    """Flow edge response."""
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None


class FlowExecutionRequest(BaseModel):
    """Request to execute a flow."""
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input values for the flow")
    run_name: Optional[str] = None
    async_mode: bool = Field(default=True, description="Run asynchronously")


class FlowExecutionResponse(BaseModel):
    """Flow execution response."""
    execution_id: str
    flow_id: str
    status: str  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    node_results: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)


class FlowNodeTypesResponse(BaseModel):
    """Available node types response."""
    categories: List[Dict[str, Any]]


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


@router.post("/{flow_id}/execute", response_model=FlowExecutionResponse)
async def execute_flow(
    flow_id: str,
    request: FlowExecutionRequest,
    background_tasks: BackgroundTasks,
) -> FlowExecutionResponse:
    """
    Execute a flow.
    
    In async mode (default), starts execution in background and returns immediately.
    In sync mode, waits for completion before returning.
    """
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # Create execution record
    execution_id = str(uuid.uuid4())
    execution = {
        "execution_id": execution_id,
        "flow_id": flow_id,
        "status": "pending",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "completed_at": None,
        "inputs": request.inputs,
        "outputs": None,
        "error": None,
        "node_results": {},
        "metrics": {},
    }
    
    _flow_executions[execution_id] = execution
    
    if request.async_mode:
        # Start execution in background
        background_tasks.add_task(_execute_flow_async, execution_id, flow, request.inputs)
        execution["status"] = "running"
    else:
        # Execute synchronously
        try:
            execution["status"] = "running"
            result = await _execute_flow(flow, request.inputs)
            execution["status"] = "completed"
            execution["outputs"] = result.get("outputs", {})
            execution["node_results"] = result.get("node_results", {})
            execution["metrics"] = result.get("metrics", {})
            execution["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return FlowExecutionResponse(**execution)


@router.get("/{flow_id}/executions", response_model=List[FlowExecutionResponse])
async def list_flow_executions(
    flow_id: str,
    limit: int = Query(10, ge=1, le=100),
) -> List[FlowExecutionResponse]:
    """List executions for a flow."""
    executions = [
        FlowExecutionResponse(**e)
        for e in _flow_executions.values()
        if e["flow_id"] == flow_id
    ]
    return executions[:limit]


@router.get("/{flow_id}/executions/{execution_id}", response_model=FlowExecutionResponse)
async def get_flow_execution(flow_id: str, execution_id: str) -> FlowExecutionResponse:
    """Get a specific flow execution."""
    execution = _flow_executions.get(execution_id)
    
    if execution is None or execution["flow_id"] != flow_id:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return FlowExecutionResponse(**execution)


# === Node Management Endpoints ===

@router.post("/{flow_id}/nodes", response_model=FlowNodeResponse)
async def add_node(flow_id: str, request: FlowNodeCreate) -> FlowNodeResponse:
    """Add a node to a flow."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # Generate node ID
    node_id = f"{request.type}-{uuid.uuid4().hex[:8]}"
    
    # Get existing metadata
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    
    # Create new node
    new_node = {
        "id": node_id,
        "type": request.type,
        "label": request.label,
        "position": request.position,
        "config": request.config,
        "description": request.description,
    }
    
    nodes.append(new_node)
    metadata["nodes"] = nodes
    
    # Update flow
    store.update_flow(flow_id, metadata=metadata)
    
    return FlowNodeResponse(**new_node)


@router.put("/{flow_id}/nodes/{node_id}", response_model=FlowNodeResponse)
async def update_node(
    flow_id: str,
    node_id: str,
    request: FlowNodeUpdate,
) -> FlowNodeResponse:
    """Update a node's configuration."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    
    # Find and update node
    for i, node in enumerate(nodes):
        if node["id"] == node_id:
            if request.label is not None:
                node["label"] = request.label
            if request.position is not None:
                node["position"] = request.position
            if request.config is not None:
                node["config"] = request.config
            if request.description is not None:
                node["description"] = request.description
            
            nodes[i] = node
            metadata["nodes"] = nodes
            store.update_flow(flow_id, metadata=metadata)
            
            return FlowNodeResponse(**node)
    
    raise HTTPException(status_code=404, detail="Node not found")


@router.delete("/{flow_id}/nodes/{node_id}")
async def delete_node(flow_id: str, node_id: str) -> dict:
    """Delete a node from a flow."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    edges = metadata.get("edges", [])
    
    # Remove node
    original_count = len(nodes)
    nodes = [n for n in nodes if n["id"] != node_id]
    
    if len(nodes) == original_count:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Remove connected edges
    edges = [e for e in edges if e["source"] != node_id and e["target"] != node_id]
    
    metadata["nodes"] = nodes
    metadata["edges"] = edges
    store.update_flow(flow_id, metadata=metadata)
    
    return {"status": "deleted", "id": node_id}


@router.get("/{flow_id}/nodes", response_model=List[FlowNodeResponse])
async def list_nodes(flow_id: str) -> List[FlowNodeResponse]:
    """List all nodes in a flow."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    
    return [FlowNodeResponse(**n) for n in nodes]


# === Edge Management Endpoints ===

@router.post("/{flow_id}/edges", response_model=FlowEdgeResponse)
async def add_edge(flow_id: str, request: FlowEdgeCreate) -> FlowEdgeResponse:
    """Add an edge between nodes."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    edges = metadata.get("edges", [])
    
    # Validate source and target exist
    node_ids = {n["id"] for n in nodes}
    if request.source not in node_ids:
        raise HTTPException(status_code=400, detail=f"Source node not found: {request.source}")
    if request.target not in node_ids:
        raise HTTPException(status_code=400, detail=f"Target node not found: {request.target}")
    
    # Create edge
    edge_id = f"edge-{uuid.uuid4().hex[:8]}"
    new_edge = {
        "id": edge_id,
        "source": request.source,
        "target": request.target,
        "source_handle": request.source_handle,
        "target_handle": request.target_handle,
    }
    
    edges.append(new_edge)
    metadata["edges"] = edges
    store.update_flow(flow_id, metadata=metadata)
    
    return FlowEdgeResponse(**new_edge)


@router.delete("/{flow_id}/edges/{edge_id}")
async def delete_edge(flow_id: str, edge_id: str) -> dict:
    """Delete an edge from a flow."""
    store = _get_store()
    flow = store.get_flow(flow_id)
    
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    metadata = flow.metadata or {}
    edges = metadata.get("edges", [])
    
    original_count = len(edges)
    edges = [e for e in edges if e["id"] != edge_id]
    
    if len(edges) == original_count:
        raise HTTPException(status_code=404, detail="Edge not found")
    
    metadata["edges"] = edges
    store.update_flow(flow_id, metadata=metadata)
    
    return {"status": "deleted", "id": edge_id}


# === Node Types Endpoint ===

@router.get("/node-types", response_model=FlowNodeTypesResponse)
async def get_node_types() -> FlowNodeTypesResponse:
    """Get available node types and their categories."""
    categories = [
        {
            "id": "flow-control",
            "name": "Flow Control",
            "description": "Control flow execution",
            "color": "from-slate-500 to-slate-600",
            "nodes": [
                {"type": "startNode", "label": "Start", "description": "Flow entry point"},
                {"type": "endNode", "label": "End", "description": "Flow exit point"},
                {"type": "conditionalNode", "label": "Conditional", "description": "Branch based on condition"},
                {"type": "loopNode", "label": "Loop", "description": "Repeat execution"},
                {"type": "parallelNode", "label": "Parallel", "description": "Execute branches in parallel"},
            ],
        },
        {
            "id": "rag",
            "name": "RAG Components",
            "description": "Retrieval-Augmented Generation",
            "color": "from-blue-500 to-cyan-500",
            "nodes": [
                {"type": "retrieverNode", "label": "Retriever", "description": "Retrieve relevant documents"},
                {"type": "rerankerNode", "label": "Reranker", "description": "Rerank retrieved documents"},
                {"type": "embeddingNode", "label": "Embedding", "description": "Generate text embeddings"},
                {"type": "vectorStoreNode", "label": "Vector Store", "description": "Store and query vectors"},
            ],
        },
        {
            "id": "llm",
            "name": "LLM Components",
            "description": "Language model operations",
            "color": "from-violet-500 to-purple-500",
            "nodes": [
                {"type": "llmNode", "label": "LLM", "description": "Generate text with LLM"},
                {"type": "promptTemplateNode", "label": "Prompt Template", "description": "Format prompts with variables"},
                {"type": "chatModelNode", "label": "Chat Model", "description": "Conversational LLM"},
            ],
        },
        {
            "id": "evaluation",
            "name": "Evaluation",
            "description": "Quality assessment",
            "color": "from-amber-500 to-orange-500",
            "nodes": [
                {"type": "llmJudgeNode", "label": "LLM Judge", "description": "Evaluate output quality"},
                {"type": "faithfulnessNode", "label": "Faithfulness", "description": "Check answer faithfulness"},
                {"type": "relevanceNode", "label": "Relevance", "description": "Check answer relevance"},
            ],
        },
        {
            "id": "hitl",
            "name": "Human-in-the-Loop",
            "description": "Human intervention points",
            "color": "from-green-500 to-emerald-500",
            "nodes": [
                {"type": "humanReviewNode", "label": "Human Review", "description": "Queue for human review"},
                {"type": "approvalGateNode", "label": "Approval Gate", "description": "Require human approval"},
                {"type": "feedbackNode", "label": "Feedback", "description": "Collect human feedback"},
            ],
        },
        {
            "id": "tools",
            "name": "Tools",
            "description": "External tool integrations",
            "color": "from-rose-500 to-pink-500",
            "nodes": [
                {"type": "toolNode", "label": "Tool", "description": "Execute a tool"},
                {"type": "apiCallNode", "label": "API Call", "description": "Make HTTP API request"},
                {"type": "codeExecutorNode", "label": "Code Executor", "description": "Execute code snippet"},
            ],
        },
        {
            "id": "data",
            "name": "Data",
            "description": "Data sources and sinks",
            "color": "from-teal-500 to-cyan-600",
            "nodes": [
                {"type": "dataSourceNode", "label": "Data Source", "description": "Read from data source"},
                {"type": "dataSinkNode", "label": "Data Sink", "description": "Write to destination"},
                {"type": "transformNode", "label": "Transform", "description": "Transform data"},
            ],
        },
        {
            "id": "orchestration",
            "name": "Orchestration",
            "description": "Workflow orchestration",
            "color": "from-indigo-500 to-blue-600",
            "nodes": [
                {"type": "prefectTaskNode", "label": "Prefect Task", "description": "Prefect workflow task"},
            ],
        },
    ]
    
    return FlowNodeTypesResponse(categories=categories)


# === Legacy Run Endpoint (for backwards compatibility) ===

@router.post("/{flow_id}/run")
async def run_flow(
    flow_id: str,
    inputs: dict = None,
    background_tasks: BackgroundTasks = None,
) -> dict:
    """Run a flow (legacy endpoint, use /execute instead)."""
    request = FlowExecutionRequest(inputs=inputs or {}, async_mode=True)
    response = await execute_flow(flow_id, request, background_tasks)
    return {
        "status": response.status,
        "execution_id": response.execution_id,
        "flow_id": flow_id,
    }


# === Helper Functions for Execution ===

async def _execute_flow(flow: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a flow and return results."""
    logger.info(f"Executing flow: {flow.name}")
    
    # Parse flow metadata for nodes and edges
    metadata = flow.metadata or {}
    nodes = metadata.get("nodes", [])
    edges = metadata.get("edges", [])
    
    if not nodes:
        # Fall back to YAML-based execution
        return await _execute_yaml_flow(flow, inputs)
    
    # Execute node-based flow
    return await _execute_node_flow(nodes, edges, inputs)


async def _execute_yaml_flow(flow: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a YAML-defined flow."""
    try:
        from agentic_assistants.adapters import get_adapter
        
        flow_def = yaml.safe_load(flow.flow_yaml) if flow.flow_yaml else {}
        flow_type = flow.flow_type or "crew"
        
        # Get appropriate adapter
        adapter = get_adapter(flow_type)
        
        # Run through adapter
        result = await asyncio.to_thread(adapter.run, flow_def, inputs)
        
        return {
            "outputs": {"result": result},
            "node_results": {},
            "metrics": {},
        }
    except Exception as e:
        logger.error(f"YAML flow execution failed: {e}")
        raise


async def _execute_node_flow(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute a node-based flow."""
    from agentic_assistants.pipelines.nodes import (
        BaseFlowNode,
        RetrieverNode, LLMNode, PromptTemplateNode,
        LLMJudgeNode, FaithfulnessNode, RelevanceNode,
        HumanReviewNode, ApprovalGateNode, FeedbackNode,
        ToolNode, APICallNode, CodeExecutorNode,
        DataSourceNode, DataSinkNode, TransformNode,
    )
    
    # Node type to class mapping
    node_classes = {
        "retrieverNode": RetrieverNode,
        "llmNode": LLMNode,
        "promptTemplateNode": PromptTemplateNode,
        "llmJudgeNode": LLMJudgeNode,
        "faithfulnessNode": FaithfulnessNode,
        "relevanceNode": RelevanceNode,
        "humanReviewNode": HumanReviewNode,
        "approvalGateNode": ApprovalGateNode,
        "feedbackNode": FeedbackNode,
        "toolNode": ToolNode,
        "apiCallNode": APICallNode,
        "codeExecutorNode": CodeExecutorNode,
        "dataSourceNode": DataSourceNode,
        "dataSinkNode": DataSinkNode,
        "transformNode": TransformNode,
    }
    
    # Build execution order (simple topological sort)
    # For now, execute in order they appear
    node_results = {}
    all_metrics = {}
    current_inputs = inputs
    
    for node_def in nodes:
        node_type = node_def.get("type")
        node_id = node_def.get("id")
        config = node_def.get("config", {})
        
        if node_type in ("startNode", "endNode"):
            continue
        
        node_class = node_classes.get(node_type)
        if not node_class:
            logger.warning(f"Unknown node type: {node_type}")
            continue
        
        try:
            # Create node instance
            config_class = node_class.config_class
            node_config = config_class(
                node_id=node_id,
                label=node_def.get("label", ""),
                **config,
            )
            node = node_class(config=node_config)
            
            # Execute node
            result = node.run(current_inputs)
            
            node_results[node_id] = {
                "success": result.success,
                "outputs": result.outputs,
                "duration_ms": result.duration_ms,
                "error": result.error_message,
            }
            
            # Collect metrics
            for key, value in result.metrics.items():
                all_metrics[f"{node_id}/{key}"] = value
            
            # Pass outputs to next node
            if result.success:
                current_inputs = {**current_inputs, **result.outputs}
            
        except Exception as e:
            logger.error(f"Node {node_id} execution failed: {e}")
            node_results[node_id] = {
                "success": False,
                "outputs": {},
                "error": str(e),
            }
    
    return {
        "outputs": current_inputs,
        "node_results": node_results,
        "metrics": all_metrics,
    }


def _execute_flow_async(execution_id: str, flow: Any, inputs: Dict[str, Any]) -> None:
    """Execute flow in background (sync wrapper)."""
    import asyncio
    
    execution = _flow_executions.get(execution_id)
    if not execution:
        return
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_execute_flow(flow, inputs))
        
        execution["status"] = "completed"
        execution["outputs"] = result.get("outputs", {})
        execution["node_results"] = result.get("node_results", {})
        execution["metrics"] = result.get("metrics", {})
        execution["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
    except Exception as e:
        logger.error(f"Flow execution failed: {e}")
        execution["status"] = "failed"
        execution["error"] = str(e)
        execution["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    finally:
        loop.close()

