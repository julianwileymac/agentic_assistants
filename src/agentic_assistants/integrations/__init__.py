"""
Integrations module for Agentic Assistants.

This module provides integrations with external services:
- JupyterManager: Manage JupyterLab instances and kernels
- MLFlowManager: Enhanced MLFlow management with model registry

Example:
    >>> from agentic_assistants.integrations import JupyterManager
    >>> 
    >>> jupyter = JupyterManager()
    >>> jupyter.ensure_running()
"""

from agentic_assistants.integrations.jupyter import JupyterManager

__all__ = [
    "JupyterManager",
]



