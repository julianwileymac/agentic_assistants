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

New in 0.3.0:
    >>> from agentic_assistants.crews import RepositoryIndexingCrew
    >>> from agentic_assistants.embeddings import EmbeddingProvider
    >>> from agentic_assistants.patterns import RAGPattern, ReActPattern
    >>> 
    >>> # Multi-agent repository indexing
    >>> crew = RepositoryIndexingCrew()
    >>> result = crew.run("./my-repo", collection="my-project")
    >>> 
    >>> # Parameterized embeddings
    >>> provider = EmbeddingProvider.create("ollama", model="nomic-embed-text")
    >>> embedding = provider.embed("Hello world")
    >>> 
    >>> # Design patterns
    >>> rag = RAGPattern(vector_store=store)
    >>> answer = rag.query("How does auth work?")
"""

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, track_experiment
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer
from agentic_assistants.core.session import Session, SessionManager
from agentic_assistants.engine import AgenticEngine
from agentic_assistants.workspace import JupyterWorkspace, workspace

# Lazy imports for new modules to avoid circular dependencies
def __getattr__(name):
    """Lazy loading for new modules."""
    if name == "RepositoryIndexingCrew":
        from agentic_assistants.crews import RepositoryIndexingCrew
        return RepositoryIndexingCrew
    elif name == "EmbeddingProvider":
        from agentic_assistants.embeddings import EmbeddingProvider
        return EmbeddingProvider
    elif name == "RAGPattern":
        from agentic_assistants.patterns import RAGPattern
        return RAGPattern
    elif name == "ReActPattern":
        from agentic_assistants.patterns import ReActPattern
        return ReActPattern
    elif name == "ChainOfThoughtPattern":
        from agentic_assistants.patterns import ChainOfThoughtPattern
        return ChainOfThoughtPattern
    elif name == "CollaborationPattern":
        from agentic_assistants.patterns import CollaborationPattern
        return CollaborationPattern
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__version__ = "0.3.0"

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
    # Crews (lazy loaded)
    "RepositoryIndexingCrew",
    # Embeddings (lazy loaded)
    "EmbeddingProvider",
    # Patterns (lazy loaded)
    "RAGPattern",
    "ReActPattern",
    "ChainOfThoughtPattern",
    "CollaborationPattern",
    # Utilities
    "track_experiment",
    "get_tracer",
    # Version
    "__version__",
]

