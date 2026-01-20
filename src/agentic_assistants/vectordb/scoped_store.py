"""
Scoped vector store wrapper for multi-level collection management.

This module provides a wrapper around vector stores that automatically
handles scoping (global, user, project, experiment) for collections.

Example:
    >>> from agentic_assistants.vectordb import ScopedVectorStore, VectorStoreScope
    >>> 
    >>> # Create a scoped store for a project
    >>> store = ScopedVectorStore(project_id="proj-123")
    >>> 
    >>> # Add documents to project scope
    >>> store.add(documents, collection="codebase")
    >>> 
    >>> # Search across scopes
    >>> results = store.search("authentication", include_global=True)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, SearchResult, VectorStore
from agentic_assistants.vectordb.config import (
    CollectionConfig,
    ScopedVectorConfig,
    VectorStoreContext,
    VectorStoreScope,
    get_collection_name,
    parse_collection_name,
)

logger = get_logger(__name__)


class ScopedVectorStore:
    """
    Scope-aware vector store wrapper.
    
    This wrapper provides automatic scoping for vector store operations,
    handling collection naming, path management, and cross-scope searches.
    
    Attributes:
        context: Current vector store context
        config: Scoped vector configuration
        store: Underlying vector store instance
    
    Example:
        >>> # Project-scoped operations
        >>> store = ScopedVectorStore(project_id="proj-123")
        >>> store.add(docs, collection="code")
        >>> 
        >>> # Search in project scope
        >>> results = store.search("function", collection="code")
        >>> 
        >>> # Search including global
        >>> results = store.search("function", include_global=True)
        >>> 
        >>> # Experiment-scoped operations
        >>> exp_store = ScopedVectorStore(
        ...     project_id="proj-123",
        ...     experiment_id="exp-456"
        ... )
        >>> exp_store.add(docs, collection="training_data")
    """
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        session_id: Optional[str] = None,
        scope: Optional[VectorStoreScope] = None,
        config: Optional[AgenticConfig] = None,
        scoped_config: Optional[ScopedVectorConfig] = None,
    ):
        """
        Initialize scoped vector store.
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            experiment_id: Experiment identifier
            session_id: Session identifier
            scope: Default scope (auto-detected if None)
            config: Application configuration
            scoped_config: Scoped vector configuration
        """
        self._config = config or AgenticConfig()
        self._scoped_config = scoped_config or self._build_scoped_config()
        
        # Determine default scope based on provided identifiers
        if scope:
            default_scope = scope
        elif experiment_id:
            default_scope = VectorStoreScope.EXPERIMENT
        elif project_id:
            default_scope = VectorStoreScope.PROJECT
        elif user_id:
            default_scope = VectorStoreScope.USER
        else:
            default_scope = VectorStoreScope.GLOBAL
        
        # Create context
        self.context = VectorStoreContext(
            scope=default_scope,
            user_id=user_id,
            project_id=project_id,
            experiment_id=experiment_id,
            session_id=session_id,
            track_lineage=self._config.vectordb.track_lineage,
        )
        
        self._store: Optional[VectorStore] = None
        self._stores_by_scope: Dict[VectorStoreScope, VectorStore] = {}
    
    def _build_scoped_config(self) -> ScopedVectorConfig:
        """Build scoped config from app config."""
        return ScopedVectorConfig(
            default_backend=self._config.vectordb.backend,
            default_embedding_model=self._config.vectordb.embedding_model,
            default_embedding_dimension=self._config.vectordb.embedding_dimension,
            global_namespace=self._config.vectordb.global_namespace,
            user_namespace_template=self._config.vectordb.user_namespace_template,
            project_namespace_template=self._config.vectordb.project_namespace_template,
            experiment_namespace_template=self._config.vectordb.experiment_namespace_template,
            enable_cross_scope_search=self._config.vectordb.enable_cross_scope_search,
            enable_scope_inheritance=self._config.vectordb.enable_scope_inheritance,
        )
    
    @property
    def store(self) -> VectorStore:
        """Get the underlying vector store for the current scope."""
        if self._store is None:
            self._store = self._get_store_for_scope(self.context.scope)
        return self._store
    
    def _get_store_for_scope(self, scope: VectorStoreScope) -> VectorStore:
        """Get or create a store for a specific scope."""
        if scope in self._stores_by_scope:
            return self._stores_by_scope[scope]
        
        # Determine storage path based on scope
        path = self._scoped_config.get_storage_path(
            scope=scope,
            user_id=self.context.user_id,
            project_id=self.context.project_id,
            base_path=self._config.vectordb.path,
        )
        
        # Create store
        store = VectorStore.create(
            backend=self._config.vectordb.backend,
            config=self._config,
            path=path,
        )
        
        self._stores_by_scope[scope] = store
        return store
    
    def _get_scoped_collection_name(
        self,
        collection: str,
        scope: Optional[VectorStoreScope] = None,
    ) -> str:
        """Get the full collection name with scope prefix."""
        scope = scope or self.context.scope
        
        return get_collection_name(
            base_name=collection,
            scope=scope,
            user_id=self.context.user_id,
            project_id=self.context.project_id,
            experiment_id=self.context.experiment_id,
            config=self._scoped_config,
        )
    
    def add(
        self,
        documents: Union[Document, List[Document]],
        collection: str = "default",
        scope: Optional[VectorStoreScope] = None,
        generate_embeddings: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Add documents to a scoped collection.
        
        Args:
            documents: Document or list of documents
            collection: Base collection name
            scope: Override scope (uses context scope if None)
            generate_embeddings: Whether to generate embeddings
            metadata: Additional metadata to add to all documents
            
        Returns:
            List of document IDs that were added
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_collection = self._get_scoped_collection_name(collection, scope)
        
        # Ensure documents is a list
        if isinstance(documents, Document):
            documents = [documents]
        
        # Add scope metadata
        if metadata or self.context.metadata:
            for doc in documents:
                doc.metadata.update(metadata or {})
                doc.metadata.update({
                    "scope": scope.value,
                    "user_id": self.context.user_id,
                    "project_id": self.context.project_id,
                    "experiment_id": self.context.experiment_id,
                })
        
        return store.add(
            documents=documents,
            collection=full_collection,
            generate_embeddings=generate_embeddings,
        )
    
    def search(
        self,
        query: Union[str, List[float]],
        collection: str = "default",
        scope: Optional[VectorStoreScope] = None,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_global: bool = False,
        include_parent_scopes: bool = False,
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query (text or embedding)
            collection: Base collection name
            scope: Override scope
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            include_global: Also search global collections
            include_parent_scopes: Search parent scopes (project includes global, etc.)
            
        Returns:
            List of SearchResult objects
        """
        scope = scope or self.context.scope
        results = []
        
        # Search in specified scope
        store = self._get_store_for_scope(scope)
        full_collection = self._get_scoped_collection_name(collection, scope)
        
        scope_results = store.search(
            query=query,
            collection=full_collection,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )
        results.extend(scope_results)
        
        # Optionally search global scope
        if include_global and scope != VectorStoreScope.GLOBAL:
            global_store = self._get_store_for_scope(VectorStoreScope.GLOBAL)
            global_collection = self._get_scoped_collection_name(
                collection, VectorStoreScope.GLOBAL
            )
            
            try:
                global_results = global_store.search(
                    query=query,
                    collection=global_collection,
                    top_k=top_k,
                    filter_metadata=filter_metadata,
                )
                results.extend(global_results)
            except Exception as e:
                logger.debug(f"Global collection search failed: {e}")
        
        # Handle scope inheritance
        if include_parent_scopes and self._scoped_config.enable_scope_inheritance:
            parent_scopes = self._get_parent_scopes(scope)
            for parent_scope in parent_scopes:
                parent_store = self._get_store_for_scope(parent_scope)
                parent_collection = self._get_scoped_collection_name(
                    collection, parent_scope
                )
                
                try:
                    parent_results = parent_store.search(
                        query=query,
                        collection=parent_collection,
                        top_k=top_k,
                        filter_metadata=filter_metadata,
                    )
                    results.extend(parent_results)
                except Exception as e:
                    logger.debug(f"Parent scope search failed: {e}")
        
        # Sort by score and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
    
    def _get_parent_scopes(self, scope: VectorStoreScope) -> List[VectorStoreScope]:
        """Get parent scopes for inheritance."""
        hierarchy = {
            VectorStoreScope.EXPERIMENT: [VectorStoreScope.PROJECT, VectorStoreScope.GLOBAL],
            VectorStoreScope.PROJECT: [VectorStoreScope.GLOBAL],
            VectorStoreScope.USER: [VectorStoreScope.GLOBAL],
            VectorStoreScope.GLOBAL: [],
        }
        return hierarchy.get(scope, [])
    
    def delete(
        self,
        document_ids: Union[str, List[str]],
        collection: str = "default",
        scope: Optional[VectorStoreScope] = None,
    ) -> int:
        """
        Delete documents by ID.
        
        Args:
            document_ids: Document ID or list of IDs
            collection: Base collection name
            scope: Override scope
            
        Returns:
            Number of documents deleted
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_collection = self._get_scoped_collection_name(collection, scope)
        
        return store.delete(document_ids, full_collection)
    
    def get(
        self,
        document_id: str,
        collection: str = "default",
        scope: Optional[VectorStoreScope] = None,
    ) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            collection: Base collection name
            scope: Override scope
            
        Returns:
            Document or None if not found
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_collection = self._get_scoped_collection_name(collection, scope)
        
        return store.get(document_id, full_collection)
    
    def list_collections(
        self,
        scope: Optional[VectorStoreScope] = None,
        include_all_scopes: bool = False,
    ) -> List[str]:
        """
        List collections.
        
        Args:
            scope: Scope to list (uses context scope if None)
            include_all_scopes: List collections from all accessible scopes
            
        Returns:
            List of collection names
        """
        if include_all_scopes:
            all_collections = []
            for s in VectorStoreScope:
                try:
                    store = self._get_store_for_scope(s)
                    collections = store.list_collections()
                    all_collections.extend(collections)
                except Exception:
                    pass
            return list(set(all_collections))
        
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        return store.list_collections()
    
    def create_collection(
        self,
        name: str,
        scope: Optional[VectorStoreScope] = None,
        config: Optional[CollectionConfig] = None,
    ) -> bool:
        """
        Create a new collection.
        
        Args:
            name: Base collection name
            scope: Override scope
            config: Collection configuration
            
        Returns:
            True if created, False if already exists
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_name = self._get_scoped_collection_name(name, scope)
        
        metadata = None
        if config:
            metadata = {
                "description": config.description,
                "track_lineage": config.track_lineage,
                "read_only": config.read_only,
                **config.metadata,
            }
        
        return store.create_collection(full_name, metadata)
    
    def delete_collection(
        self,
        name: str,
        scope: Optional[VectorStoreScope] = None,
    ) -> bool:
        """
        Delete a collection.
        
        Args:
            name: Base collection name
            scope: Override scope
            
        Returns:
            True if deleted, False if not found
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_name = self._get_scoped_collection_name(name, scope)
        
        return store.delete_collection(full_name)
    
    def count(
        self,
        collection: str = "default",
        scope: Optional[VectorStoreScope] = None,
    ) -> int:
        """
        Get document count in a collection.
        
        Args:
            collection: Base collection name
            scope: Override scope
            
        Returns:
            Document count
        """
        scope = scope or self.context.scope
        store = self._get_store_for_scope(scope)
        full_collection = self._get_scoped_collection_name(collection, scope)
        
        return store.count(full_collection)
    
    def get_info(self) -> Dict[str, Any]:
        """Get scoped store information."""
        return {
            "context": self.context.to_dict(),
            "scoped_config": {
                "default_backend": self._scoped_config.default_backend,
                "enable_cross_scope_search": self._scoped_config.enable_cross_scope_search,
                "enable_scope_inheritance": self._scoped_config.enable_scope_inheritance,
            },
            "stores": {
                scope.value: store.get_info() if store else None
                for scope, store in self._stores_by_scope.items()
            },
        }
    
    def with_scope(
        self,
        scope: VectorStoreScope,
        **kwargs,
    ) -> "ScopedVectorStore":
        """
        Create a new store with a different scope.
        
        Args:
            scope: New scope
            **kwargs: Override context values
            
        Returns:
            New ScopedVectorStore instance
        """
        return ScopedVectorStore(
            user_id=kwargs.get("user_id", self.context.user_id),
            project_id=kwargs.get("project_id", self.context.project_id),
            experiment_id=kwargs.get("experiment_id", self.context.experiment_id),
            session_id=kwargs.get("session_id", self.context.session_id),
            scope=scope,
            config=self._config,
            scoped_config=self._scoped_config,
        )
    
    def global_store(self) -> "ScopedVectorStore":
        """Get a store scoped to global."""
        return self.with_scope(VectorStoreScope.GLOBAL)
    
    def project_store(self, project_id: Optional[str] = None) -> "ScopedVectorStore":
        """Get a store scoped to a project."""
        return self.with_scope(
            VectorStoreScope.PROJECT,
            project_id=project_id or self.context.project_id,
        )
    
    def experiment_store(
        self,
        experiment_id: str,
        project_id: Optional[str] = None,
    ) -> "ScopedVectorStore":
        """Get a store scoped to an experiment."""
        return self.with_scope(
            VectorStoreScope.EXPERIMENT,
            experiment_id=experiment_id,
            project_id=project_id or self.context.project_id,
        )


def create_scoped_store(
    project_id: Optional[str] = None,
    user_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    config: Optional[AgenticConfig] = None,
) -> ScopedVectorStore:
    """
    Factory function to create a scoped vector store.
    
    Args:
        project_id: Project identifier
        user_id: User identifier
        experiment_id: Experiment identifier
        config: Application configuration
        
    Returns:
        ScopedVectorStore instance
    """
    return ScopedVectorStore(
        project_id=project_id,
        user_id=user_id,
        experiment_id=experiment_id,
        config=config,
    )
