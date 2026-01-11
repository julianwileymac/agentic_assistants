# Chunk: 091ceea00cab_0

- source: `src/agentic_assistants/knowledge/hybrid_kb.py`
- lines: 1-95
- chunk: 1/4

```
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
```
