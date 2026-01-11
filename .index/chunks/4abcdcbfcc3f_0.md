# Chunk: 4abcdcbfcc3f_0

- source: `src/agentic_assistants/server/api/flows.py`
- lines: 1-101
- chunk: 1/4

```
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
```
