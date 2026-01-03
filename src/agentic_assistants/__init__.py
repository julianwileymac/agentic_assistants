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
"""

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, track_experiment
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer

__version__ = "0.1.0"

__all__ = [
    # Configuration
    "AgenticConfig",
    # Core components
    "OllamaManager",
    "MLFlowTracker",
    "TelemetryManager",
    # Utilities
    "track_experiment",
    "get_tracer",
    # Version
    "__version__",
]

