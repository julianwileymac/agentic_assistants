# Chunk: 4abcdcbfcc3f_1

- source: `src/agentic_assistants/server/api/flows.py`
- lines: 90-169
- chunk: 2/4

```
rors = []
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
```
