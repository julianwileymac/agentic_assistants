"""
RAG (Retrieval-Augmented Generation) nodes.

This module provides flow nodes for RAG pipelines:
- RetrieverNode: Query documents from vector stores
- RerankerNode: Rerank retrieved documents
- EmbeddingNode: Generate text embeddings
- VectorStoreNode: Interact with vector stores

Example:
    >>> from agentic_assistants.pipelines.nodes import RetrieverNode
    >>> 
    >>> retriever = RetrieverNode(config=RetrieverConfig(
    ...     collection="my_docs",
    ...     top_k=5,
    ...     min_score=0.7,
    ... ))
    >>> 
    >>> result = retriever.run({"query": "What is RAG?"})
    >>> print(result.outputs["documents"])
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class RetrieverConfig(NodeConfig):
    """Configuration for RetrieverNode."""
    
    # Vector store collection to query
    collection: str = "default"
    
    # Number of documents to retrieve
    top_k: int = 5
    
    # Minimum similarity score threshold
    min_score: float = 0.7
    
    # Optional metadata filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Vector store ID (for external stores)
    vector_store_id: Optional[str] = None
    
    # Whether to include document content
    include_content: bool = True
    
    # Whether to include metadata
    include_metadata: bool = True


@dataclass
class RerankerConfig(NodeConfig):
    """Configuration for RerankerNode."""
    
    # Reranker model to use
    model: str = "cross-encoder"
    
    # Number of documents to return after reranking
    top_n: int = 3
    
    # Minimum score after reranking
    min_score: float = 0.5
    
    # Model-specific options
    model_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingConfig(NodeConfig):
    """Configuration for EmbeddingNode."""
    
    # Embedding model to use
    model: str = "nomic-embed-text"
    
    # Expected embedding dimensions
    dimensions: Optional[int] = None
    
    # Batch size for embedding generation
    batch_size: int = 32
    
    # Whether to normalize embeddings
    normalize: bool = True


@dataclass
class VectorStoreConfig(NodeConfig):
    """Configuration for VectorStoreNode."""
    
    # Collection name
    collection: str = "default"
    
    # Operation type: upsert, delete, search, count
    operation: str = "search"
    
    # Index type for new collections
    index_type: str = "hnsw"
    
    # Distance metric
    distance_metric: str = "cosine"


# =============================================================================
# Node Implementations
# =============================================================================

class RetrieverNode(BaseFlowNode):
    """
    Node for retrieving documents from a vector store.
    
    Inputs:
        query: The search query (string or embedding)
        
    Outputs:
        documents: List of retrieved documents
        scores: List of similarity scores
    """
    
    node_type = "retriever"
    config_class = RetrieverConfig
    
    def __init__(self, config: Optional[RetrieverConfig] = None, **kwargs):
        super().__init__(config or RetrieverConfig(), **kwargs)
        self.config: RetrieverConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        
        if not query:
            return {"documents": [], "scores": []}
        
        try:
            # Import vector store client
            from agentic_assistants.vectordb import get_vectordb
            
            db = get_vectordb()
            
            # Perform search
            results = db.search(
                collection=self.config.collection,
                query=query,
                top_k=self.config.top_k,
                filters=self.config.filters or None,
            )
            
            # Filter by min score
            filtered_results = [
                r for r in results 
                if r.get("score", 0) >= self.config.min_score
            ]
            
            documents = []
            scores = []
            
            for r in filtered_results:
                doc = {}
                if self.config.include_content:
                    doc["content"] = r.get("content", "")
                if self.config.include_metadata:
                    doc["metadata"] = r.get("metadata", {})
                doc["id"] = r.get("id", "")
                documents.append(doc)
                scores.append(r.get("score", 0))
            
            # Emit metrics
            self.emit_metric("documents_retrieved", len(documents))
            if scores:
                self.emit_metric("avg_score", sum(scores) / len(scores))
                self.emit_metric("top_score", max(scores))
            
            # Emit RL metric for retrieval quality
            if scores:
                self.emit_rl_metric("retrieval_relevance", sum(scores) / len(scores))
            
            return {
                "documents": documents,
                "scores": scores,
            }
            
        except ImportError:
            logger.warning("Vector DB not available, returning empty results")
            return {"documents": [], "scores": []}
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "metadata": {"type": "object"},
                        },
                    },
                },
                "scores": {
                    "type": "array",
                    "items": {"type": "number"},
                },
            },
        }


class RerankerNode(BaseFlowNode):
    """
    Node for reranking retrieved documents.
    
    Inputs:
        query: The original query
        documents: List of documents to rerank
        
    Outputs:
        documents: Reranked documents
        scores: New relevance scores
    """
    
    node_type = "reranker"
    config_class = RerankerConfig
    
    def __init__(self, config: Optional[RerankerConfig] = None, **kwargs):
        super().__init__(config or RerankerConfig(), **kwargs)
        self.config: RerankerConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        documents = inputs.get("documents", [])
        
        if not query or not documents:
            return {"documents": [], "scores": []}
        
        try:
            # Simple reranking using cross-encoder or similar
            # In production, use a proper reranker model
            
            # For now, return documents as-is with placeholder scores
            # Real implementation would use sentence-transformers CrossEncoder
            reranked = documents[:self.config.top_n]
            scores = [1.0 - (i * 0.1) for i in range(len(reranked))]
            
            # Filter by min score
            filtered = [
                (doc, score) 
                for doc, score in zip(reranked, scores)
                if score >= self.config.min_score
            ]
            
            result_docs = [d for d, _ in filtered]
            result_scores = [s for _, s in filtered]
            
            # Emit metrics
            self.emit_metric("documents_reranked", len(result_docs))
            if result_scores:
                self.emit_metric("avg_rerank_score", sum(result_scores) / len(result_scores))
            
            return {
                "documents": result_docs,
                "scores": result_scores,
            }
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "documents": {"type": "array"},
            },
            "required": ["query", "documents"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "documents": {"type": "array"},
                "scores": {"type": "array", "items": {"type": "number"}},
            },
        }


class EmbeddingNode(BaseFlowNode):
    """
    Node for generating text embeddings.
    
    Inputs:
        texts: List of texts to embed
        
    Outputs:
        embeddings: List of embedding vectors
    """
    
    node_type = "embedding"
    config_class = EmbeddingConfig
    
    def __init__(self, config: Optional[EmbeddingConfig] = None, **kwargs):
        super().__init__(config or EmbeddingConfig(), **kwargs)
        self.config: EmbeddingConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        texts = inputs.get("texts", [])
        
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return {"embeddings": []}
        
        try:
            # Import embedding model
            from langchain_ollama import OllamaEmbeddings
            
            embeddings_model = OllamaEmbeddings(model=self.config.model)
            
            # Generate embeddings in batches
            all_embeddings = []
            for i in range(0, len(texts), self.config.batch_size):
                batch = texts[i:i + self.config.batch_size]
                batch_embeddings = embeddings_model.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
            
            # Emit metrics
            self.emit_metric("texts_embedded", len(texts))
            if all_embeddings:
                self.emit_metric("embedding_dimensions", len(all_embeddings[0]))
            
            return {"embeddings": all_embeddings}
            
        except ImportError:
            logger.warning("Embedding model not available")
            return {"embeddings": []}
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "texts": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                },
            },
            "required": ["texts"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "embeddings": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                },
            },
        }


class VectorStoreNode(BaseFlowNode):
    """
    Node for vector store operations.
    
    Inputs:
        documents: Documents to upsert (for upsert operation)
        embeddings: Embeddings for the documents
        ids: Document IDs (for delete operation)
        query: Search query (for search operation)
        
    Outputs:
        result: Operation result
    """
    
    node_type = "vector_store"
    config_class = VectorStoreConfig
    
    def __init__(self, config: Optional[VectorStoreConfig] = None, **kwargs):
        super().__init__(config or VectorStoreConfig(), **kwargs)
        self.config: VectorStoreConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from agentic_assistants.vectordb import get_vectordb
            
            db = get_vectordb()
            
            if self.config.operation == "upsert":
                documents = inputs.get("documents", [])
                embeddings = inputs.get("embeddings")
                
                result = db.upsert(
                    collection=self.config.collection,
                    documents=documents,
                    embeddings=embeddings,
                )
                
                self.emit_metric("documents_upserted", len(documents))
                return {"result": result, "count": len(documents)}
            
            elif self.config.operation == "delete":
                ids = inputs.get("ids", [])
                
                result = db.delete(
                    collection=self.config.collection,
                    ids=ids,
                )
                
                self.emit_metric("documents_deleted", len(ids))
                return {"result": result, "count": len(ids)}
            
            elif self.config.operation == "search":
                query = inputs.get("query", "")
                top_k = inputs.get("top_k", 5)
                
                results = db.search(
                    collection=self.config.collection,
                    query=query,
                    top_k=top_k,
                )
                
                return {"result": results}
            
            elif self.config.operation == "count":
                count = db.count(collection=self.config.collection)
                return {"result": count, "count": count}
            
            else:
                raise ValueError(f"Unknown operation: {self.config.operation}")
            
        except ImportError:
            logger.warning("Vector DB not available")
            return {"result": None, "error": "Vector DB not available"}
        except Exception as e:
            logger.error(f"Vector store operation failed: {e}")
            raise
