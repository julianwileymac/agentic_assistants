"""
Vector-based knowledge base implementation.
"""

import hashlib
from typing import Any, Dict, List, Optional

from agentic_assistants.knowledge.base import (
    KnowledgeBase,
    KnowledgeBaseConfig,
    SearchResult,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class VectorKnowledgeBase(KnowledgeBase):
    """
    Knowledge base backed by a vector store.
    
    Provides semantic search over documents using embeddings.
    
    Example:
        >>> kb = VectorKnowledgeBase(KnowledgeBaseConfig(name="docs"))
        >>> kb.add_documents(["Document 1 content", "Document 2 content"])
        >>> results = kb.search("relevant query")
    """
    
    def __init__(self, config: Optional[KnowledgeBaseConfig] = None):
        """
        Initialize vector knowledge base.
        
        Args:
            config: Knowledge base configuration
        """
        config = config or KnowledgeBaseConfig()
        super().__init__(config)
        
        self._vector_store = None
    
    @property
    def vector_store(self):
        """Get or create vector store."""
        if self._vector_store is None:
            try:
                from agentic_assistants.vectordb import LanceDBStore
                from agentic_assistants.config import AgenticConfig
                
                app_config = AgenticConfig()
                self._vector_store = LanceDBStore(
                    db_path=str(app_config.vectordb.db_path),
                    embedding_model=self.config.embedding_model,
                )
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                raise
        
        return self._vector_store
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search the knowledge base."""
        k = top_k or self.config.top_k
        
        try:
            results = self.vector_store.search(
                collection=self.config.collection,
                query=query,
                top_k=k,
                filters=filters,
            )
            
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    content=result.get("content", result.get("text", "")),
                    score=result.get("score", result.get("distance", 0.0)),
                    metadata=result.get("metadata", {}),
                    source=result.get("metadata", {}).get("source", ""),
                    chunk_id=result.get("id"),
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def query(
        self,
        question: str,
        context_docs: Optional[int] = None,
    ) -> str:
        """
        Query with basic retrieval (no generation).
        
        For RAG with generation, use RAGKnowledgeBase.
        """
        results = self.search(question, top_k=context_docs)
        
        if not results:
            return "No relevant information found."
        
        # Return concatenated results
        contents = [r.content for r in results]
        return "\n\n---\n\n".join(contents)
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """Add documents to the knowledge base."""
        if not documents:
            return 0
        
        # Generate IDs if not provided
        if ids is None:
            ids = [
                hashlib.sha256(doc.encode()).hexdigest()[:16]
                for doc in documents
            ]
        
        # Use empty metadata if not provided
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        try:
            self.vector_store.add(
                collection=self.config.collection,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            
            logger.info(f"Added {len(documents)} documents to {self.config.collection}")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return 0
    
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Delete documents from the knowledge base."""
        try:
            if ids:
                self.vector_store.delete(
                    collection=self.config.collection,
                    ids=ids,
                )
                return len(ids)
            
            # For filter-based deletion, need to search first
            if filters:
                results = self.search("", top_k=1000, filters=filters)
                ids_to_delete = [r.chunk_id for r in results if r.chunk_id]
                if ids_to_delete:
                    self.vector_store.delete(
                        collection=self.config.collection,
                        ids=ids_to_delete,
                    )
                return len(ids_to_delete)
            
            # Clear all - delete collection
            self.vector_store.delete_collection(self.config.collection)
            return -1  # Unknown count
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return 0
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            result = self.vector_store.get(
                collection=self.config.collection,
                ids=[doc_id],
            )
            if result:
                return result[0]
            return None
        except Exception:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            count = self.vector_store.count(self.config.collection)
        except Exception:
            count = 0
        
        return {
            "type": "vector",
            "name": self.name,
            "collection": self.config.collection,
            "document_count": count,
            "embedding_model": self.config.embedding_model,
            "initialized": self._initialized,
        }
