"""
Agent framework adapters with built-in observability.

These adapters wrap popular agent frameworks to provide:
- MLFlow experiment tracking
- OpenTelemetry tracing
- Usage tracking for meta-analysis
- RAG knowledge base integration
- Persistent memory support
- Standardized interfaces

Supported frameworks:
- CrewAI: Multi-agent crew orchestration
- LangGraph: Graph-based workflow orchestration
- AutoGen: Microsoft's multi-agent conversation framework
- Google ADK: Google's Agent Development Kit
- Agno: Modern agent framework with reasoning modes
- LangFlow: Visual workflow builder for LangChain
- Prefect: Workflow orchestration for data and ML pipelines
- Dagster: Asset-oriented data orchestration and scheduling

Example:
    >>> from agentic_assistants.adapters import CrewAIAdapter, LangGraphAdapter
    >>> 
    >>> # Create an adapter with observability
    >>> adapter = CrewAIAdapter()
    >>> 
    >>> # Connect RAG and memory
    >>> from agentic_assistants.knowledge import get_knowledge_base
    >>> adapter.connect_rag(get_knowledge_base("my_project"))
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run_crew(crew, inputs={"topic": "AI"})
"""

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.adapters.crewai_adapter import CrewAIAdapter
from agentic_assistants.adapters.langgraph_adapter import LangGraphAdapter
from agentic_assistants.adapters.autogen_adapter import AutoGenAdapter
from agentic_assistants.adapters.google_adk_adapter import GoogleADKAdapter
from agentic_assistants.adapters.agno_adapter import AgnoAdapter
from agentic_assistants.adapters.langflow_adapter import LangFlowAdapter
from agentic_assistants.adapters.prefect_adapter import PrefectAdapter
from agentic_assistants.adapters.dagster_adapter import DagsterAdapter

__all__ = [
    # Base
    "BaseAdapter",
    # Framework adapters
    "CrewAIAdapter",
    "LangGraphAdapter",
    "AutoGenAdapter",
    "GoogleADKAdapter",
    "AgnoAdapter",
    "LangFlowAdapter",
    "PrefectAdapter",
    "DagsterAdapter",
]


def get_adapter(framework: str, **kwargs) -> BaseAdapter:
    """
    Get an adapter for the specified framework.
    
    Args:
        framework: Framework name (crewai, langgraph, autogen, google_adk, agno, langflow, prefect)
        **kwargs: Additional arguments passed to the adapter
        
    Returns:
        Configured adapter instance
        
    Raises:
        ValueError: If framework is not supported
    """
    adapters = {
        "crewai": CrewAIAdapter,
        "langgraph": LangGraphAdapter,
        "autogen": AutoGenAdapter,
        "google_adk": GoogleADKAdapter,
        "agno": AgnoAdapter,
        "langflow": LangFlowAdapter,
        "prefect": PrefectAdapter,
        "dagster": DagsterAdapter,
    }
    
    framework_lower = framework.lower()
    if framework_lower not in adapters:
        raise ValueError(
            f"Unknown framework: {framework}. "
            f"Supported: {', '.join(adapters.keys())}"
        )
    
    return adapters[framework_lower](**kwargs)


def list_frameworks() -> list:
    """List all supported frameworks."""
    return ["crewai", "langgraph", "autogen", "google_adk", "agno", "langflow", "prefect", "dagster"]

