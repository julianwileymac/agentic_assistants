"""
Serving backends.
"""

from agentic_assistants.serving.backends.ollama import OllamaBackend, DeploymentResult

__all__ = ["OllamaBackend", "DeploymentResult"]
