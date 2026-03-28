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
- datasources: Data source management
- kubernetes: Kubernetes cluster management
- learning: Learning goals, topics, and lesson plans
- evaluations: Learning assessments and grading
- framework_assistant: Framework Assistant Agent API
- ollama: Ollama model management
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
from agentic_assistants.server.api.datasources import router as datasources_router
from agentic_assistants.server.api.generation import router as generation_router
from agentic_assistants.server.api.kubernetes import router as kubernetes_router
from agentic_assistants.server.api.docs import router as docs_router
from agentic_assistants.server.api.assistant import router as assistant_router
from agentic_assistants.server.api.learning import router as learning_router
from agentic_assistants.server.api.evaluations import router as evaluations_router
from agentic_assistants.server.api.framework_assistant import router as framework_assistant_router
from agentic_assistants.server.api.ollama import router as ollama_router
from agentic_assistants.server.api.testing import router as testing_router
from agentic_assistants.server.api.huggingface import router as huggingface_router

# Additional routers (execution, sync, cybersec, lineage, cache, upload, memory, discovery)
from agentic_assistants.server.api.execution import router as execution_router
from agentic_assistants.server.api.sync import router as sync_router
from agentic_assistants.server.api.cybersec import router as cybersec_router
from agentic_assistants.server.api.lineage import router as lineage_router
from agentic_assistants.server.api.cache import router as cache_router
from agentic_assistants.server.api.upload import router as upload_router
from agentic_assistants.server.api.memory import router as memory_router
from agentic_assistants.server.api.discovery import router as discovery_router

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
    "datasources_router",
    "generation_router",
    "docs_router",
    "assistant_router",
    "testing_router",
    # Infrastructure routers
    "kubernetes_router",
    # Learning routers
    "learning_router",
    "evaluations_router",
    # Framework Assistant routers
    "framework_assistant_router",
    "ollama_router",
    "huggingface_router",
    # Additional routers
    "execution_router",
    "sync_router",
    "cybersec_router",
    "lineage_router",
    "cache_router",
    "upload_router",
    "memory_router",
    "discovery_router",
]
