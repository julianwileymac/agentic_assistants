"""
Vector database module for Agentic Assistants.

This module provides:
- VectorStore: Abstract base class for vector database operations
- LanceDBStore: LanceDB implementation (embedded, local-first)
- ChromaDBStore: ChromaDB implementation (server or embedded)
- VectorStoreScope: Enum for vector store scoping (global, user, project, experiment)
- ScopedVectorConfig: Configuration for scoped vector operations

Example:
    >>> from agentic_assistants.vectordb import VectorStore, VectorStoreScope
    >>> 
    >>> store = VectorStore.create("lancedb", path="./data/vectors")
    >>> store.add(documents, collection="codebase")
    >>> results = store.search("authentication flow", top_k=5)
    >>> 
    >>> # Scoped operations
    >>> from agentic_assistants.vectordb import get_collection_name
    >>> name = get_collection_name("docs", VectorStoreScope.PROJECT, project_id="proj-123")
"""

from agentic_assistants.vectordb.base import VectorStore, Document, SearchResult
from agentic_assistants.vectordb.lancedb_store import LanceDBStore
from agentic_assistants.vectordb.config import (
    VectorStoreScope,
    CollectionConfig,
    ScopedVectorConfig,
    VectorStoreContext,
    get_collection_name,
    parse_collection_name,
)

__all__ = [
    # Base classes
    "VectorStore",
    "Document",
    "SearchResult",
    "LanceDBStore",
    # Scoping
    "VectorStoreScope",
    "CollectionConfig",
    "ScopedVectorConfig",
    "VectorStoreContext",
    "get_collection_name",
    "parse_collection_name",
]


# Lazy import for ChromaDB to avoid dependency issues
def get_chroma_store():
    """Get ChromaDB store class (lazy import)."""
    from agentic_assistants.vectordb.chroma_store import ChromaDBStore
    return ChromaDBStore


# Lazy import for scoped store
def get_scoped_store():
    """Get ScopedVectorStore class (lazy import)."""
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    return ScopedVectorStore

