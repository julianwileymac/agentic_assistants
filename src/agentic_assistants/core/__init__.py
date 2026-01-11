"""
Core components for Agentic Assistants.

This module contains the fundamental building blocks:
- OllamaManager: Manage Ollama server and models
- MLFlowTracker: Experiment tracking integration
- MLFlowManager: Enhanced model registry and deployment
- TelemetryManager: OpenTelemetry observability
"""

from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import (
    MLFlowTracker,
    MLFlowManager,
    track_experiment,
    ModelStage,
    ModelVersion,
    DeploymentTarget,
    DeploymentInfo,
)
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer

__all__ = [
    "OllamaManager",
    "MLFlowTracker",
    "MLFlowManager",
    "track_experiment",
    "ModelStage",
    "ModelVersion",
    "DeploymentTarget",
    "DeploymentInfo",
    "TelemetryManager",
    "get_tracer",
]

