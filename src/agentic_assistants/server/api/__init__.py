"""
API routers for Agentic Assistants.

This module provides modular FastAPI routers for different components:
- experiments: MLFlow experiment management
- artifacts: Artifact storage and management
- sessions: Session lifecycle and persistence
- data: Data layer operations
- config: Runtime configuration management
"""

from agentic_assistants.server.api.experiments import router as experiments_router
from agentic_assistants.server.api.artifacts import router as artifacts_router
from agentic_assistants.server.api.sessions import router as sessions_router
from agentic_assistants.server.api.data import router as data_router
from agentic_assistants.server.api.config import router as config_router

__all__ = [
    "experiments_router",
    "artifacts_router",
    "sessions_router",
    "data_router",
    "config_router",
]

