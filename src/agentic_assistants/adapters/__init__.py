"""
Agent framework adapters with built-in observability.

These adapters wrap popular agent frameworks to provide:
- MLFlow experiment tracking
- OpenTelemetry tracing
- Standardized interfaces
"""

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.adapters.crewai_adapter import CrewAIAdapter
from agentic_assistants.adapters.langgraph_adapter import LangGraphAdapter
from agentic_assistants.adapters.huggingface_adapter import HuggingFaceAdapter
from agentic_assistants.adapters.smolagents_adapter import SmolAgentsAdapter

__all__ = [
    "BaseAdapter",
    "CrewAIAdapter",
    "LangGraphAdapter",
    "HuggingFaceAdapter",
    "SmolAgentsAdapter",
]
