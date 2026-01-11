"""
Hybrid knowledge base combining multiple data sources.
"""

from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.knowledge.base import (
    KnowledgeBase,
    KnowledgeBaseConfig,
    SearchResult,
)
from agentic_assistants.knowledge.vector_kb import VectorKnowledgeBase
from agentic_assistants.knowledge.rag_kb import RAGKnowledgeBase
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class HybridKnowledgeBase(KnowledgeBase):
    """
    Hybrid knowledge base that combines vector search with structured data.
    
    Features:
    - Vector search for semantic similarity
    - Feature store integration for structured features
    - Data catalog integration for datasets
    - Optional reranking for better results
    - RAG generation
    
    Example:
        >>> kb = HybridKnowledgeBase(KnowledgeBaseConfig(
        ...     name="project_kb",
        ...     data_sources=["source1", "source2"],
        ...     feature_views=["user_features"]
        ... ))
        >>> results = kb.search("user behavior patterns")
    """
    
    def __init__(
        self,
        config: Optional[KnowledgeBaseConfig] = None,
        llm_fn: Optional[Callable] = None,
    ):
        """
        Initialize hybrid knowledge base.
        
        Args:
            config: Knowledge base configuration
            llm_fn: Custom LLM function
        """
        config = config or KnowledgeBaseConfig()
        super().__init__(config)
        
        # Core RAG KB for vector search and generation
        self._rag_kb = RAGKnowledgeBase(config, llm_fn)
        
        # Reranker (optional)
        self._reranker = None
        if config.use_reranking:
            self._init_reranker()
        
        # Caches for integrated sources
        self._data_source_cache: Dict[str, Any] = {}
        self._feature_cache: Dict[str, Any] = {}
    
    def _init_reranker(self) -> None:
        """Initialize reranking model."""
        try:
            from sentence_transformers import CrossEncoder
            
            model_name = self.config.rerank_model or "cross-encoder/ms-marco-MiniLM-L-6-v2"
            self._reranker = CrossEncoder(model_name)
            logger.info(f"Initialized reranker: {model_name}")
            
        except ImportError:
            logger.warning("sentence-transformers required for reranking")
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        rerank: Optional[bool] = None,
    ) -> List[SearchResult]:
        """
        Search the knowledge base with optional reranking.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters
            rerank: Override reranking setting
            
        Returns:
            List of search results
        """
        k = top_k or self.config.top_k
        
        # Get more results for reranking
        fetch_k = k * 3 if (rerank or self.config.use_reranking) else k
        
        # Vector search
        results = self._rag_kb.search(query, top_k=fetch_k, filters=filters)
        
        # Rerank if enabled
        should_rerank = rerank if rerank is not None else self.config.use_reranking
        if should_rerank and self._reranker and len(results) > 1:
            results = self._rerank_results(query, results)
        
        return results[:k]
    
    def _rerank_results(
        self,
        query: str,
        results: List[SearchResult],
    ) -> List[SearchResult]:
        """Rerank results using cross-encoder."""
        if not self._reranker:
            return results
        
        # Prepare pairs for reranking
        pairs = [(query, r.content) for r in results]
        
        # Get reranking scores
        scores = self._reranker.predict(pairs)
        
        # Update scores and sort
        for result, score in zip(results, scores):
            result.score = float(score)
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def query(
        self,
        question: str,
        context_docs: Optional[int] = None,
        include_features: bool = False,
    ) -> str:
        """
        Query the knowledge base with RAG.
        
        Args:
            question: Question to answer
            context_docs: Number of context documents
            include_features: Include feature store data in context
            
        Returns:
            Generated answer
        """
        # Get vector search results
        k = context_docs or self.config.top_k
        results = self.search(question, top_k=k)
        
        # Build context
        context_parts = []
        
        # Add vector search results
        for i, result in enumerate(results, 1):
            source = result.source or f"Source {i}"
            context_parts.append(f"[{source}]\n{result.content}")
        
        # Add features if requested and configured
        if include_features and self.config.feature_views:
            feature_context = self._get_feature_context(question)
            if feature_context:
                context_parts.append(f"[Feature Data]\n{feature_context}")
        
        # Generate answer
        if not context_parts:
            return "I couldn't find any relevant information."
        
        context = "\n\n".join(context_parts)
        
        # Use RAG KB for generation
        self._rag_kb._vector_kb = self._rag_kb._vector_kb  # Ensure same vector store
        prompt = self._rag_kb.query_template.format(
            context=context,
            question=question,
        )
        
        return self._rag_kb.llm_fn(prompt)
    
    def _get_feature_context(self, query: str) -> str:
        """Get relevant features for context."""
        try:
            from agentic_assistants.features import get_feature_store
            
            store = get_feature_store()
            
            context_parts = []
            for view_name in self.config.feature_views:
                view = store.get_feature_view(view_name)
                if view:
                    context_parts.append(
                        f"Feature View '{view_name}' contains: "
                        f"{', '.join(view.feature_names)}"
                    )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.debug(f"Could not get feature context: {e}")
            return ""
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """Add documents to the knowledge base."""
        return self._rag_kb.add_documents(documents, metadatas, ids)
    
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Delete documents from the knowledge base."""
        return self._rag_kb.delete_documents(ids, filters)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self._rag_kb.get_document(doc_id)
    
    def add_from_data_source(self, source_id: str) -> int:
        """Add documents from a data source."""
        try:
            from agentic_assistants.data.catalog import DataCatalog
            from agentic_assistants.data.rag import IngestionPipeline
            
            catalog = DataCatalog()
            
            # Get dataset from catalog
            data = catalog.load(source_id)
            
            if data is None:
                return 0
            
            # Use ingestion pipeline
            pipeline = IngestionPipeline()
            
            if isinstance(data, str):
                result = pipeline.ingest(
                    source=data,
                    source_type="text",
                    collection=self.config.collection,
                )
                return result.chunks_stored
            elif isinstance(data, dict):
                # Convert to text
                text = "\n".join(f"{k}: {v}" for k, v in data.items())
                result = pipeline.ingest(
                    source=text,
                    source_type="text",
                    collection=self.config.collection,
                )
                return result.chunks_stored
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to add from data source: {e}")
            return 0
    
    def add_from_dataset(self, dataset_name: str, text_column: str) -> int:
        """Add documents from a dataset."""
        try:
            from agentic_assistants.data.catalog import DataCatalog
            
            catalog = DataCatalog()
            
            # Load dataset
            df = catalog.load(dataset_name)
            
            if df is None or text_column not in df.columns:
                return 0
            
            # Extract texts
            documents = df[text_column].dropna().astype(str).tolist()
            
            # Build metadata from other columns
            metadatas = []
            for _, row in df.iterrows():
                metadata = {
                    col: str(row[col])
                    for col in df.columns
                    if col != text_column and row[col] is not None
                }
                metadata["dataset"] = dataset_name
                metadatas.append(metadata)
            
            return self.add_documents(documents, metadatas)
            
        except Exception as e:
            logger.error(f"Failed to add from dataset: {e}")
            return 0
    
    def sync_data_sources(self) -> Dict[str, int]:
        """Sync all configured data sources."""
        results = {}
        
        for source_id in self.config.data_sources:
            count = self.add_from_data_source(source_id)
            results[source_id] = count
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        base_stats = self._rag_kb.get_stats()
        
        return {
            **base_stats,
            "type": "hybrid",
            "data_sources": self.config.data_sources,
            "datasets": self.config.datasets,
            "feature_views": self.config.feature_views,
            "use_reranking": self.config.use_reranking,
            "reranker_available": self._reranker is not None,
        }
