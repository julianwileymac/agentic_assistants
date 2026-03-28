"""
Data Transfer Objects for the FastAPI REST API.

Provides typed request/response schemas that enforce API boundaries,
preventing internal model details from leaking to consumers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from agentic_assistants.core.base_models import AgenticBaseModel, ErrorResponse, PaginatedResponse


# === Project DTOs ===

class ProjectCreateDTO(AgenticBaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    status: str = "active"
    tags: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class ProjectReadDTO(AgenticBaseModel):
    id: str
    name: str
    description: str
    status: str
    tags: list[str]
    config: dict[str, Any]
    created_at: str
    updated_at: Optional[str] = None


class ProjectUpdateDTO(AgenticBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
    config: Optional[dict[str, Any]] = None


# === Agent DTOs ===

class AgentCreateDTO(AgenticBaseModel):
    name: str = Field(min_length=1, max_length=255)
    role: str = ""
    goal: str = ""
    backstory: str = ""
    model: str = ""
    tools: list[str] = Field(default_factory=list)
    project_id: Optional[str] = None


class AgentReadDTO(AgenticBaseModel):
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    model: str
    tools: list[str]
    project_id: Optional[str]
    created_at: str


class AgentUpdateDTO(AgenticBaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[list[str]] = None


# === Flow DTOs ===

class FlowCreateDTO(AgenticBaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    flow_type: str = "sequential"
    yaml_config: str = ""
    agent_ids: list[str] = Field(default_factory=list)
    project_id: Optional[str] = None


class FlowReadDTO(AgenticBaseModel):
    id: str
    name: str
    description: str
    flow_type: str
    yaml_config: str
    agent_ids: list[str]
    project_id: Optional[str]
    created_at: str


class FlowUpdateDTO(AgenticBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flow_type: Optional[str] = None
    yaml_config: Optional[str] = None
    agent_ids: Optional[list[str]] = None


# === Component DTOs ===

class ComponentCreateDTO(AgenticBaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = ""
    code: str = ""
    language: str = "python"
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class ComponentReadDTO(AgenticBaseModel):
    id: str
    name: str
    category: str
    code: str
    language: str
    description: str
    tags: list[str]
    version: int = 1
    created_at: str


# === DataSource DTOs ===

class DataSourceCreateDTO(AgenticBaseModel):
    name: str = Field(min_length=1, max_length=255)
    ds_type: str = ""
    connection_config: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class DataSourceReadDTO(AgenticBaseModel):
    id: str
    name: str
    ds_type: str
    description: str
    created_at: str


# === Generic Response DTOs ===

class PaginatedResponseDTO(PaginatedResponse[Any]):
    """Generic paginated API response wrapper."""


class StatusResponseDTO(AgenticBaseModel):
    status: str = "ok"
    message: str = ""


class ErrorResponseDTO(ErrorResponse):
    """Standard API error response."""


__all__ = [
    "ProjectCreateDTO", "ProjectReadDTO", "ProjectUpdateDTO",
    "AgentCreateDTO", "AgentReadDTO", "AgentUpdateDTO",
    "FlowCreateDTO", "FlowReadDTO", "FlowUpdateDTO",
    "ComponentCreateDTO", "ComponentReadDTO",
    "DataSourceCreateDTO", "DataSourceReadDTO",
    "PaginatedResponseDTO", "StatusResponseDTO", "ErrorResponseDTO",
]
