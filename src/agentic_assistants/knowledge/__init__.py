"""
Knowledge Base System for Agent Data Access.

This module provides a unified knowledge base system that agents can use
to access various data sources, vector stores, and RAG systems.

Example:
    >>> from agentic_assistants.knowledge import KnowledgeBase, get_knowledge_base
    >>> 
    >>> # Get a project knowledge base
    >>> kb = get_knowledge_base("my_project")
    >>> 
    >>> # Search for relevant information
    >>> results = kb.search("machine learning concepts")
    >>> 
    >>> # Get RAG-augmented response
    >>> response = kb.query("What are neural networks?")
"""

from agentic_assistants.knowledge.base import (
    KnowledgeBase,
    KnowledgeBaseConfig,
    SearchResult,
)
from agentic_assistants.knowledge.vector_kb import VectorKnowledgeBase
from agentic_assistants.knowledge.rag_kb import RAGKnowledgeBase
from agentic_assistants.knowledge.hybrid_kb import HybridKnowledgeBase


# Registry of knowledge bases
_knowledge_bases: dict = {}


def get_knowledge_base(
    name: str,
    config: KnowledgeBaseConfig = None,
    kb_type: str = "hybrid",
) -> KnowledgeBase:
    """
    Get or create a knowledge base.
    
    Args:
        name: Knowledge base name
        config: Configuration (uses defaults if None)
        kb_type: Type of knowledge base (vector, rag, hybrid)
        
    Returns:
        Knowledge base instance
    """
    if name not in _knowledge_bases:
        if config is None:
            config = KnowledgeBaseConfig(name=name)
        
        if kb_type == "vector":
            _knowledge_bases[name] = VectorKnowledgeBase(config)
        elif kb_type == "rag":
            _knowledge_bases[name] = RAGKnowledgeBase(config)
        else:
            _knowledge_bases[name] = HybridKnowledgeBase(config)
    
    return _knowledge_bases[name]


def list_knowledge_bases() -> list:
    """List all registered knowledge base names."""
    return list(_knowledge_bases.keys())


__all__ = [
    # Base classes
    "KnowledgeBase",
    "KnowledgeBaseConfig",
    "SearchResult",
    # Implementations
    "VectorKnowledgeBase",
    "RAGKnowledgeBase",
    "HybridKnowledgeBase",
    # Functions
    "get_knowledge_base",
    "list_knowledge_bases",
]
