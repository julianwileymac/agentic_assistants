"""
Vector database module for Agentic Assistants.

This module provides:
- VectorStore: Abstract base class for vector database operations
- LanceDBStore: LanceDB implementation (embedded, local-first)
- ChromaDBStore: ChromaDB implementation (server or embedded)

Example:
    >>> from agentic_assistants.vectordb import VectorStore
    >>> 
    >>> store = VectorStore.create("lancedb", path="./data/vectors")
    >>> store.add(documents, collection="codebase")
    >>> results = store.search("authentication flow", top_k=5)
"""

from agentic_assistants.vectordb.base import VectorStore, Document, SearchResult
from agentic_assistants.vectordb.lancedb_store import LanceDBStore

__all__ = [
    "VectorStore",
    "Document",
    "SearchResult",
    "LanceDBStore",
]

# Lazy import for ChromaDB to avoid dependency issues
def get_chroma_store():
    """Get ChromaDB store class (lazy import)."""
    from agentic_assistants.vectordb.chroma_store import ChromaDBStore
    return ChromaDBStore

