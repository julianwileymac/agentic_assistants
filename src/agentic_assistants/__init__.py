"""
Agentic Assistants - A local framework for multi-agent experimentation.

This package provides tools for experimenting with multi-agent frameworks like
CrewAI and LangGraph, with integrated MLOps tooling via MLFlow and OpenTelemetry.

Example usage:
    >>> from agentic_assistants import AgenticConfig, OllamaManager
    >>> from agentic_assistants.adapters import CrewAIAdapter
    >>>
    >>> config = AgenticConfig()
    >>> ollama = OllamaManager(config)
    >>> ollama.ensure_running()

New in 0.2.0:
    >>> from agentic_assistants import AgenticEngine, JupyterWorkspace
    >>> 
    >>> # Use the unified engine
    >>> engine = AgenticEngine()
    >>> engine.index_codebase("./src")
    >>> results = engine.search("authentication")
    >>> 
    >>> # Or use the Jupyter workspace
    >>> with JupyterWorkspace("my-session") as ws:
    ...     ws.index("./data")
    ...     ws.search("relevant docs")
"""

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, track_experiment
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer
from agentic_assistants.core.session import Session, SessionManager
from agentic_assistants.engine import AgenticEngine
from agentic_assistants.workspace import JupyterWorkspace, workspace

__version__ = "0.2.0"

__all__ = [
    # Configuration
    "AgenticConfig",
    # Core components
    "OllamaManager",
    "MLFlowTracker",
    "TelemetryManager",
    # Session management
    "Session",
    "SessionManager",
    # Engine and Workspace
    "AgenticEngine",
    "JupyterWorkspace",
    "workspace",
    # Utilities
    "track_experiment",
    "get_tracer",
    # Version
    "__version__",
]

