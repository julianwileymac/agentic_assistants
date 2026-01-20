"""
Vector store pipeline nodes for document ingestion and retrieval.

This module provides reusable pipeline nodes for vector store operations,
making it easy to integrate vector storage into data pipelines.

Example:
    >>> from agentic_assistants.pipelines.nodes import (
    ...     vectorstore_upsert_node,
    ...     VectorStoreOutputConfig,
    ... )
    >>> 
    >>> # Use in a pipeline
    >>> config = VectorStoreOutputConfig(
    ...     collection="documents",
    ...     scope="project",
    ...     project_id="proj-123",
    ... )
    >>> result = vectorstore_upsert_node(documents, config.to_dict())
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class VectorStoreOutputConfig(BaseModel):
    """Configuration for vector store output in pipelines."""
    
    # Collection settings
    collection: str = Field(
        default="default",
        description="Collection name",
    )
    scope: str = Field(
        default="project",
        description="Vector store scope (global, user, project, experiment)",
    )
    
    # Scoping identifiers
    project_id: Optional[str] = Field(
        default=None,
        description="Project ID for project/experiment scope",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID for user scope",
    )
    experiment_id: Optional[str] = Field(
        default=None,
        description="Experiment ID for experiment scope",
    )
    
    # Embedding settings
    generate_embeddings: bool = Field(
        default=True,
        description="Generate embeddings for documents",
    )
    embedding_model: Optional[str] = Field(
        default=None,
        description="Override embedding model",
    )
    
    # Behavior settings
    upsert: bool = Field(
        default=True,
        description="Update existing documents (vs error on duplicate)",
    )
    batch_size: int = Field(
        default=100,
        description="Batch size for insertion",
    )
    
    # Lineage tracking
    track_lineage: bool = Field(
        default=True,
        description="Track document lineage",
    )
    pipeline_name: Optional[str] = Field(
        default=None,
        description="Pipeline name for lineage",
    )
    pipeline_run_id: Optional[str] = Field(
        default=None,
        description="Pipeline run ID for lineage",
    )
    
    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="Tags to add to all documents",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for all documents",
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for pipeline use."""
        return {
            "collection": self.collection,
            "scope": self.scope,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "experiment_id": self.experiment_id,
            "generate_embeddings": self.generate_embeddings,
            "embedding_model": self.embedding_model,
            "upsert": self.upsert,
            "batch_size": self.batch_size,
            "track_lineage": self.track_lineage,
            "pipeline_name": self.pipeline_name,
            "pipeline_run_id": self.pipeline_run_id,
            "tags": self.tags,
            "metadata": self.metadata,
        }


def vectorstore_upsert_node(
    documents: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pipeline node for upserting documents to a vector store.
    
    Args:
        documents: List of document dictionaries with 'content' and optional 'metadata'
        config: VectorStoreOutputConfig as dictionary
        
    Returns:
        Dictionary with operation results
        
    Example:
        >>> docs = [
        ...     {"content": "Document 1", "metadata": {"source": "file1.txt"}},
        ...     {"content": "Document 2", "metadata": {"source": "file2.txt"}},
        ... ]
        >>> config = {"collection": "docs", "scope": "project", "project_id": "proj-123"}
        >>> result = vectorstore_upsert_node(docs, config)
    """
    from agentic_assistants.vectordb import Document, VectorStoreScope
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    
    if not documents:
        return {
            "success": True,
            "documents_added": 0,
            "collection": config.get("collection", "default"),
        }
    
    # Parse scope
    scope_str = config.get("scope", "project")
    try:
        scope = VectorStoreScope(scope_str)
    except ValueError:
        scope = VectorStoreScope.PROJECT
    
    # Create scoped store
    store = ScopedVectorStore(
        project_id=config.get("project_id"),
        user_id=config.get("user_id"),
        experiment_id=config.get("experiment_id"),
        scope=scope,
    )
    
    # Prepare documents
    doc_objects = []
    base_metadata = config.get("metadata", {})
    tags = config.get("tags", [])
    
    for i, doc in enumerate(documents):
        # Handle different document formats
        if isinstance(doc, str):
            content = doc
            metadata = {}
        elif isinstance(doc, dict):
            content = doc.get("content", doc.get("text", ""))
            metadata = doc.get("metadata", {})
        else:
            continue
        
        if not content:
            continue
        
        # Merge metadata
        final_metadata = {
            **base_metadata,
            **metadata,
            "tags": list(set(tags + metadata.get("tags", []))),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
        }
        
        if config.get("track_lineage"):
            final_metadata["pipeline_name"] = config.get("pipeline_name")
            final_metadata["pipeline_run_id"] = config.get("pipeline_run_id")
        
        doc_obj = Document(
            id=doc.get("id", f"doc_{i}_{hash(content) % 10000}"),
            content=content,
            metadata=final_metadata,
        )
        doc_objects.append(doc_obj)
    
    # Batch insert
    batch_size = config.get("batch_size", 100)
    collection = config.get("collection", "default")
    total_added = 0
    errors = []
    
    for i in range(0, len(doc_objects), batch_size):
        batch = doc_objects[i:i + batch_size]
        try:
            ids = store.add(
                documents=batch,
                collection=collection,
                generate_embeddings=config.get("generate_embeddings", True),
            )
            total_added += len(ids)
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            errors.append(str(e))
    
    logger.info(f"Upserted {total_added} documents to {collection}")
    
    return {
        "success": len(errors) == 0,
        "documents_added": total_added,
        "collection": collection,
        "scope": scope.value,
        "errors": errors,
    }


def vectorstore_delete_node(
    document_ids: List[str],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pipeline node for deleting documents from a vector store.
    
    Args:
        document_ids: List of document IDs to delete
        config: Configuration dictionary
        
    Returns:
        Dictionary with operation results
    """
    from agentic_assistants.vectordb import VectorStoreScope
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    
    if not document_ids:
        return {
            "success": True,
            "documents_deleted": 0,
            "collection": config.get("collection", "default"),
        }
    
    # Parse scope
    scope_str = config.get("scope", "project")
    try:
        scope = VectorStoreScope(scope_str)
    except ValueError:
        scope = VectorStoreScope.PROJECT
    
    # Create scoped store
    store = ScopedVectorStore(
        project_id=config.get("project_id"),
        user_id=config.get("user_id"),
        experiment_id=config.get("experiment_id"),
        scope=scope,
    )
    
    collection = config.get("collection", "default")
    
    try:
        count = store.delete(document_ids, collection=collection)
        logger.info(f"Deleted {count} documents from {collection}")
        
        return {
            "success": True,
            "documents_deleted": count,
            "collection": collection,
        }
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return {
            "success": False,
            "documents_deleted": 0,
            "collection": collection,
            "error": str(e),
        }


def vectorstore_search_node(
    query: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pipeline node for searching a vector store.
    
    Args:
        query: Search query
        config: Configuration dictionary
        
    Returns:
        Dictionary with search results
    """
    from agentic_assistants.vectordb import VectorStoreScope
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    
    # Parse scope
    scope_str = config.get("scope", "project")
    try:
        scope = VectorStoreScope(scope_str)
    except ValueError:
        scope = VectorStoreScope.PROJECT
    
    # Create scoped store
    store = ScopedVectorStore(
        project_id=config.get("project_id"),
        user_id=config.get("user_id"),
        experiment_id=config.get("experiment_id"),
        scope=scope,
    )
    
    collection = config.get("collection", "default")
    top_k = config.get("top_k", 5)
    include_global = config.get("include_global", False)
    filter_metadata = config.get("filter_metadata")
    
    try:
        results = store.search(
            query=query,
            collection=collection,
            top_k=top_k,
            include_global=include_global,
            filter_metadata=filter_metadata,
        )
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "content": r.document.content,
                    "score": r.score,
                    "metadata": r.document.metadata,
                    "id": r.document.id,
                }
                for r in results
            ],
            "count": len(results),
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e),
        }


def vectorstore_create_collection_node(
    collection_name: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pipeline node for creating a vector store collection.
    
    Args:
        collection_name: Name of the collection to create
        config: Configuration dictionary
        
    Returns:
        Dictionary with operation results
    """
    from agentic_assistants.vectordb import VectorStoreScope
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    
    # Parse scope
    scope_str = config.get("scope", "project")
    try:
        scope = VectorStoreScope(scope_str)
    except ValueError:
        scope = VectorStoreScope.PROJECT
    
    # Create scoped store
    store = ScopedVectorStore(
        project_id=config.get("project_id"),
        user_id=config.get("user_id"),
        experiment_id=config.get("experiment_id"),
        scope=scope,
    )
    
    try:
        created = store.create_collection(collection_name)
        
        return {
            "success": True,
            "collection": collection_name,
            "created": created,
            "scope": scope.value,
        }
    except Exception as e:
        logger.error(f"Create collection error: {e}")
        return {
            "success": False,
            "collection": collection_name,
            "created": False,
            "error": str(e),
        }


def create_vectorstore_sink_node(
    config: VectorStoreOutputConfig,
):
    """
    Create a pipeline node function configured for vector store output.
    
    This is a factory function that creates a node function with
    pre-configured settings.
    
    Args:
        config: Vector store output configuration
        
    Returns:
        Node function that accepts documents and stores them
        
    Example:
        >>> config = VectorStoreOutputConfig(
        ...     collection="docs",
        ...     scope="project",
        ...     project_id="proj-123",
        ... )
        >>> sink_node = create_vectorstore_sink_node(config)
        >>> result = sink_node(documents)
    """
    config_dict = config.to_dict()
    
    def sink_node(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        return vectorstore_upsert_node(documents, config_dict)
    
    return sink_node


def vectorstore_count_node(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pipeline node to get document count in a collection.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary with count result
    """
    from agentic_assistants.vectordb import VectorStoreScope
    from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
    
    # Parse scope
    scope_str = config.get("scope", "project")
    try:
        scope = VectorStoreScope(scope_str)
    except ValueError:
        scope = VectorStoreScope.PROJECT
    
    # Create scoped store
    store = ScopedVectorStore(
        project_id=config.get("project_id"),
        user_id=config.get("user_id"),
        experiment_id=config.get("experiment_id"),
        scope=scope,
    )
    
    collection = config.get("collection", "default")
    
    try:
        count = store.count(collection)
        
        return {
            "success": True,
            "collection": collection,
            "count": count,
            "scope": scope.value,
        }
    except Exception as e:
        logger.error(f"Count error: {e}")
        return {
            "success": False,
            "collection": collection,
            "count": 0,
            "error": str(e),
        }
