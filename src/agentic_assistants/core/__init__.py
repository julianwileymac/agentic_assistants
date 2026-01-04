"""
Core components for Agentic Assistants.

This module contains the fundamental building blocks:
- OllamaManager: Manage Ollama server and models
- MLFlowTracker: Experiment tracking integration
- TelemetryManager: OpenTelemetry observability
- SessionManager: Persistent session management
"""

from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, track_experiment
from agentic_assistants.core.telemetry import (
    TelemetryManager,
    VerboseSpanLogger,
    get_tracer,
    get_meter,
    trace_function,
    trace_async_function,
)
from agentic_assistants.core.session import Session, SessionManager, Artifact

__all__ = [
    # Ollama
    "OllamaManager",
    # MLFlow
    "MLFlowTracker",
    "track_experiment",
    # Telemetry
    "TelemetryManager",
    "VerboseSpanLogger",
    "get_tracer",
    "get_meter",
    "trace_function",
    "trace_async_function",
    # Session
    "Session",
    "SessionManager",
    "Artifact",
]
