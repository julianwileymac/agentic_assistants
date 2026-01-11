# Chunk: 4abcdcbfcc3f_2

- source: `src/agentic_assistants/server/api/flows.py`
- lines: 157-250
- chunk: 3/4

```
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
    
```
