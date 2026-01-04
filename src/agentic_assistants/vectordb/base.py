"""
Abstract base class for vector database implementations.

This module defines the common interface that all vector store
implementations must follow.

Example:
    >>> from agentic_assistants.vectordb import VectorStore
    >>> 
    >>> store = VectorStore.create("lancedb", path="./data/vectors")
    >>> store.add(documents, collection="codebase")
    >>> results = store.search("query", top_k=5)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """
    A document to be stored in the vector database.
    
    Attributes:
        id: Unique document identifier
        content: Text content of the document
        embedding: Optional pre-computed embedding vector
        metadata: Additional metadata (file path, language, etc.)
    """
    
    id: str
    content: str
    embedding: Optional[list[float]] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SearchResult:
    """
    A search result from the vector database.
    
    Attributes:
        document: The matched document
        score: Similarity score (higher is more similar)
        distance: Distance metric (lower is more similar)
    """
    
    document: Document
    score: float = 0.0
    distance: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document": self.document.to_dict(),
            "score": self.score,
            "distance": self.distance,
        }


class VectorStore(ABC):
    """
    Abstract base class for vector database implementations.
    
    This class defines the interface that all vector stores must implement,
    providing a consistent API for adding, searching, and managing documents.
    
    Subclasses must implement:
    - _add_documents()
    - _search()
    - _delete_documents()
    - _get_document()
    - _list_collections()
    - _create_collection()
    - _delete_collection()
    
    Attributes:
        config: Agentic configuration
        embedding_model: Model used for generating embeddings
        embedding_dimension: Dimension of embedding vectors
    """

    # Registry of available backends
    _backends: dict[str, type["VectorStore"]] = {}

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        path: Optional[Union[str, Path]] = None,
        embedding_model: Optional[str] = None,
        embedding_dimension: Optional[int] = None,
    ):
        """
        Initialize the vector store.
        
        Args:
            config: Configuration instance
            path: Override path for vector storage
            embedding_model: Override embedding model
            embedding_dimension: Override embedding dimension
        """
        self.config = config or AgenticConfig()
        self.path = Path(path) if path else Path(self.config.vectordb.path)
        self.embedding_model = embedding_model or self.config.vectordb.embedding_model
        self.embedding_dimension = embedding_dimension or self.config.vectordb.embedding_dimension
        
        # Ensure path exists
        self.path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def register_backend(cls, name: str, backend_class: type["VectorStore"]) -> None:
        """Register a vector store backend."""
        cls._backends[name] = backend_class

    @classmethod
    def create(
        cls,
        backend: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ) -> "VectorStore":
        """
        Factory method to create a vector store instance.
        
        Args:
            backend: Backend name ("lancedb", "chroma")
            config: Configuration instance
            **kwargs: Additional arguments for the backend
        
        Returns:
            VectorStore instance
        
        Raises:
            ValueError: If backend is not registered
        """
        config = config or AgenticConfig()
        backend_name = backend or config.vectordb.backend
        
        if backend_name not in cls._backends:
            # Try lazy loading
            if backend_name == "lancedb":
                from agentic_assistants.vectordb.lancedb_store import LanceDBStore
                cls._backends["lancedb"] = LanceDBStore
            elif backend_name == "chroma":
                from agentic_assistants.vectordb.chroma_store import ChromaDBStore
                cls._backends["chroma"] = ChromaDBStore
            else:
                available = ", ".join(cls._backends.keys())
                raise ValueError(
                    f"Unknown vector store backend: {backend_name}. "
                    f"Available: {available}"
                )
        
        return cls._backends[backend_name](config=config, **kwargs)

    # === Public API ===

    def add(
        self,
        documents: Union[Document, list[Document]],
        collection: str = "default",
        generate_embeddings: bool = True,
    ) -> list[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: Document or list of documents to add
            collection: Collection/namespace to add to
            generate_embeddings: Whether to generate embeddings for documents
        
        Returns:
            List of document IDs that were added
        """
        if isinstance(documents, Document):
            documents = [documents]
        
        if not documents:
            return []
        
        # Ensure collection exists
        if collection not in self.list_collections():
            self.create_collection(collection)
        
        # Generate embeddings if needed
        if generate_embeddings:
            documents = self._ensure_embeddings(documents)
        
        return self._add_documents(documents, collection)

    def search(
        self,
        query: Union[str, list[float]],
        collection: str = "default",
        top_k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query (text or embedding vector)
            collection: Collection to search in
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of SearchResult objects
        """
        # Convert query to embedding if it's text
        if isinstance(query, str):
            query_embedding = self._generate_embedding(query)
        else:
            query_embedding = query
        
        return self._search(query_embedding, collection, top_k, filter_metadata)

    def delete(
        self,
        document_ids: Union[str, list[str]],
        collection: str = "default",
    ) -> int:
        """
        Delete documents by ID.
        
        Args:
            document_ids: Document ID or list of IDs to delete
            collection: Collection to delete from
        
        Returns:
            Number of documents deleted
        """
        if isinstance(document_ids, str):
            document_ids = [document_ids]
        
        return self._delete_documents(document_ids, collection)

    def get(
        self,
        document_id: str,
        collection: str = "default",
    ) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            collection: Collection to get from
        
        Returns:
            Document or None if not found
        """
        return self._get_document(document_id, collection)

    def list_collections(self) -> list[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        return self._list_collections()

    def create_collection(
        self,
        name: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            metadata: Optional collection metadata
        
        Returns:
            True if created, False if already exists
        """
        return self._create_collection(name, metadata)

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection and all its documents.
        
        Args:
            name: Collection name
        
        Returns:
            True if deleted, False if not found
        """
        return self._delete_collection(name)

    def count(self, collection: str = "default") -> int:
        """
        Get the number of documents in a collection.
        
        Args:
            collection: Collection name
        
        Returns:
            Document count
        """
        return self._count(collection)

    # === Abstract methods (must be implemented by subclasses) ===

    @abstractmethod
    def _add_documents(
        self,
        documents: list[Document],
        collection: str,
    ) -> list[str]:
        """Add documents to a collection."""
        pass

    @abstractmethod
    def _search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int,
        filter_metadata: Optional[dict],
    ) -> list[SearchResult]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def _delete_documents(
        self,
        document_ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents by ID."""
        pass

    @abstractmethod
    def _get_document(
        self,
        document_id: str,
        collection: str,
    ) -> Optional[Document]:
        """Get a document by ID."""
        pass

    @abstractmethod
    def _list_collections(self) -> list[str]:
        """List all collections."""
        pass

    @abstractmethod
    def _create_collection(
        self,
        name: str,
        metadata: Optional[dict],
    ) -> bool:
        """Create a collection."""
        pass

    @abstractmethod
    def _delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        pass

    @abstractmethod
    def _count(self, collection: str) -> int:
        """Count documents in a collection."""
        pass

    # === Embedding methods ===

    def _ensure_embeddings(self, documents: list[Document]) -> list[Document]:
        """Ensure all documents have embeddings."""
        for doc in documents:
            if doc.embedding is None:
                doc.embedding = self._generate_embedding(doc.content)
        return documents

    def _generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for text.
        
        This method uses Ollama by default but can be overridden.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            import httpx
            
            response = httpx.post(
                f"{self.config.ollama.host}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text,
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension

    # === Utility methods ===

    def get_info(self) -> dict:
        """Get information about the vector store."""
        collections = self.list_collections()
        return {
            "backend": self.__class__.__name__,
            "path": str(self.path),
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "collections": collections,
            "collection_counts": {c: self.count(c) for c in collections},
        }

