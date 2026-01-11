"""
Base classes for the Knowledge Base system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge bases."""
    
    name: str = "default"
    description: str = ""
    
    # Vector store settings
    collection: str = ""  # Uses name if empty
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # RAG settings
    llm_model: str = "llama3"
    top_k: int = 5
    max_context_length: int = 4000
    
    # Hybrid settings
    use_reranking: bool = False
    rerank_model: Optional[str] = None
    
    # Scope
    scope: str = "project"  # project, global
    project_id: Optional[str] = None
    
    # Data sources
    data_sources: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    feature_views: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.collection:
            self.collection = self.name


@dataclass
class SearchResult:
    """A single search result from the knowledge base."""
    
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    chunk_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "source": self.source,
            "chunk_id": self.chunk_id,
        }


class KnowledgeBase(ABC):
    """
    Abstract base class for knowledge bases.
    
    Knowledge bases provide:
    - Semantic search over documents
    - RAG-style query answering
    - Integration with data sources and catalogs
    - Scope management (project vs global)
    """
    
    def __init__(self, config: KnowledgeBaseConfig):
        """
        Initialize the knowledge base.
        
        Args:
            config: Knowledge base configuration
        """
        self.config = config
        self.name = config.name
        self._initialized = False
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def query(
        self,
        question: str,
        context_docs: Optional[int] = None,
    ) -> str:
        """
        Query the knowledge base with RAG.
        
        Args:
            question: Question to answer
            context_docs: Number of context documents
            
        Returns:
            Generated answer
        """
        pass
    
    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: Optional document IDs
            
        Returns:
            Number of documents added
        """
        pass
    
    @abstractmethod
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Delete documents from the knowledge base.
        
        Args:
            ids: Document IDs to delete
            filters: Metadata filters for deletion
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass
    
    def add_from_data_source(self, source_id: str) -> int:
        """
        Add documents from a data source.
        
        Args:
            source_id: Data source ID from catalog
            
        Returns:
            Number of documents added
        """
        # Implementation depends on data source type
        raise NotImplementedError("Subclass must implement add_from_data_source")
    
    def add_from_dataset(self, dataset_name: str, text_column: str) -> int:
        """
        Add documents from a dataset.
        
        Args:
            dataset_name: Dataset name from catalog
            text_column: Column containing text
            
        Returns:
            Number of documents added
        """
        # Implementation depends on dataset type
        raise NotImplementedError("Subclass must implement add_from_dataset")
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        pass
    
    def clear(self) -> int:
        """Clear all documents from the knowledge base."""
        return self.delete_documents()
