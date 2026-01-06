"""
API routers for Agentic Assistants.

This module provides modular FastAPI routers for different components:
- experiments: MLFlow experiment management
- artifacts: Artifact storage and management
- sessions: Session lifecycle and persistence
- data: Data layer operations
- config: Runtime configuration management
- projects: Project management (Control Panel)
- agents: Agent management (Control Panel)
- flows: Multi-agent flow management (Control Panel)
- components: Code component library (Control Panel)
- notes: Free-form notes (Control Panel)
- tags: Resource tagging (Control Panel)
"""

from agentic_assistants.server.api.experiments import router as experiments_router
from agentic_assistants.server.api.artifacts import router as artifacts_router
from agentic_assistants.server.api.sessions import router as sessions_router
from agentic_assistants.server.api.data import router as data_router
from agentic_assistants.server.api.config import router as config_router
from agentic_assistants.server.api.projects import router as projects_router
from agentic_assistants.server.api.agents import router as agents_router
from agentic_assistants.server.api.flows import router as flows_router
from agentic_assistants.server.api.components import router as components_router
from agentic_assistants.server.api.notes import router as notes_router
from agentic_assistants.server.api.tags import router as tags_router

__all__ = [
    # Original routers
    "experiments_router",
    "artifacts_router",
    "sessions_router",
    "data_router",
    "config_router",
    # Control Panel routers
    "projects_router",
    "agents_router",
    "flows_router",
    "components_router",
    "notes_router",
    "tags_router",
]
