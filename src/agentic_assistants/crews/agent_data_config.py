"""
Agent Data Configuration for specifying data sources and knowledge bases.

This module provides configuration classes for connecting agents to
various data sources, datasets, knowledge bases, and feature stores.

Example:
    >>> from agentic_assistants.crews.agent_data_config import AgentDataConfig
    >>> 
    >>> data_config = AgentDataConfig(
    ...     knowledge_base="project_kb",
    ...     data_sources=["github_api", "docs_dataset"],
    ...     feature_views=["user_features"],
    ... )
    >>> 
    >>> agent = factory.create_agent(
    ...     role="Analyst",
    ...     ...,
    ...     data_config=data_config,
    ... )
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentDataConfig:
    """
    Configuration for agent data access.
    
    Specifies which data sources, datasets, knowledge bases,
    and feature stores an agent can access.
    
    Attributes:
        data_sources: IDs of data sources from the catalog
        datasets: Names of datasets from the catalog
        knowledge_base: Name of the knowledge base to use
        rag_collection: Vector store collection for RAG
        feature_views: Feature store views for structured data
        enable_caching: Cache data lookups
        cache_ttl: Cache TTL in seconds
    """
    
    # Data sources from catalog
    data_sources: List[str] = field(default_factory=list)
    
    # Datasets from catalog
    datasets: List[str] = field(default_factory=list)
    
    # Knowledge base name
    knowledge_base: Optional[str] = None
    
    # RAG collection name
    rag_collection: Optional[str] = None
    
    # Feature store views
    feature_views: List[str] = field(default_factory=list)
    
    # Caching settings
    enable_caching: bool = True
    cache_ttl: int = 300
    
    # Search settings
    default_top_k: int = 5
    
    # Custom metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data_sources": self.data_sources,
            "datasets": self.datasets,
            "knowledge_base": self.knowledge_base,
            "rag_collection": self.rag_collection,
            "feature_views": self.feature_views,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "default_top_k": self.default_top_k,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDataConfig":
        """Create from dictionary."""
        return cls(**data)


class AgentDataContext:
    """
    Runtime context for agent data access.
    
    Provides methods for agents to access configured data sources,
    knowledge bases, and feature stores.
    
    Example:
        >>> context = AgentDataContext(data_config)
        >>> 
        >>> # Search knowledge base
        >>> results = context.search("relevant query")
        >>> 
        >>> # Get features for an entity
        >>> features = context.get_features({"user_id": 123})
    """
    
    def __init__(self, config: AgentDataConfig):
        """
        Initialize agent data context.
        
        Args:
            config: Agent data configuration
        """
        self.config = config
        self._knowledge_base = None
        self._feature_store = None
        self._catalog = None
        self._cache = None
    
    @property
    def knowledge_base(self):
        """Get the configured knowledge base."""
        if self._knowledge_base is None and self.config.knowledge_base:
            from agentic_assistants.knowledge import get_knowledge_base
            self._knowledge_base = get_knowledge_base(self.config.knowledge_base)
        return self._knowledge_base
    
    @property
    def feature_store(self):
        """Get the feature store."""
        if self._feature_store is None and self.config.feature_views:
            from agentic_assistants.features import get_feature_store
            self._feature_store = get_feature_store()
        return self._feature_store
    
    @property
    def catalog(self):
        """Get the data catalog."""
        if self._catalog is None:
            from agentic_assistants.data.catalog import DataCatalog
            self._catalog = DataCatalog()
        return self._catalog
    
    @property
    def cache(self):
        """Get the cache instance."""
        if self._cache is None and self.config.enable_caching:
            from agentic_assistants.data.caching import get_cache
            self._cache = get_cache()
        return self._cache
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters
            
        Returns:
            List of search results
        """
        if not self.knowledge_base:
            logger.warning("No knowledge base configured")
            return []
        
        k = top_k or self.config.default_top_k
        
        # Check cache
        if self.cache:
            cache_key = f"kb_search:{self.config.knowledge_base}:{query}:{k}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        results = self.knowledge_base.search(query, top_k=k, filters=filters)
        result_dicts = [r.to_dict() for r in results]
        
        # Cache results
        if self.cache:
            self.cache.set(cache_key, result_dicts, self.config.cache_ttl)
        
        return result_dicts
    
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
        if not self.knowledge_base:
            return "No knowledge base configured for this agent."
        
        return self.knowledge_base.query(question, context_docs)
    
    def get_features(
        self,
        entity_key: Dict[str, Any],
        feature_refs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get feature values for an entity.
        
        Args:
            entity_key: Entity identifier
            feature_refs: Specific features to get
            
        Returns:
            Dictionary of feature values
        """
        if not self.feature_store:
            logger.warning("No feature store configured")
            return {}
        
        # Build feature refs if not provided
        if feature_refs is None:
            feature_refs = []
            for view_name in self.config.feature_views:
                view = self.feature_store.get_feature_view(view_name)
                if view:
                    for feature in view.features:
                        feature_refs.append(f"{view_name}:{feature.name}")
        
        if not feature_refs:
            return {}
        
        # Get online features
        vectors = self.feature_store.get_online_features(
            feature_refs=feature_refs,
            entity_keys=[entity_key],
        )
        
        if vectors:
            return vectors[0].features
        return {}
    
    def load_dataset(self, dataset_name: str) -> Any:
        """
        Load a dataset from the catalog.
        
        Args:
            dataset_name: Dataset name
            
        Returns:
            Dataset data
        """
        if dataset_name not in self.config.datasets:
            logger.warning(f"Dataset '{dataset_name}' not in agent config")
        
        return self.catalog.load(dataset_name)
    
    def load_data_source(self, source_id: str) -> Any:
        """
        Load data from a data source.
        
        Args:
            source_id: Data source ID
            
        Returns:
            Data from source
        """
        if source_id not in self.config.data_sources:
            logger.warning(f"Data source '{source_id}' not in agent config")
        
        return self.catalog.load(source_id)


def create_search_tool(context: AgentDataContext):
    """
    Create a search tool for an agent.
    
    Args:
        context: Agent data context
        
    Returns:
        Tool function for knowledge base search
    """
    def search_knowledge_base(query: str, top_k: int = 5) -> str:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Formatted search results
        """
        results = context.search(query, top_k=top_k)
        
        if not results:
            return "No relevant results found."
        
        output = []
        for i, result in enumerate(results, 1):
            source = result.get("source", f"Source {i}")
            content = result.get("content", "")[:500]
            output.append(f"[{i}] {source}\n{content}")
        
        return "\n\n".join(output)
    
    return search_knowledge_base


def create_query_tool(context: AgentDataContext):
    """
    Create a RAG query tool for an agent.
    
    Args:
        context: Agent data context
        
    Returns:
        Tool function for RAG queries
    """
    def query_knowledge_base(question: str) -> str:
        """
        Ask a question and get an answer from the knowledge base.
        
        Args:
            question: Question to answer
            
        Returns:
            Generated answer
        """
        return context.query(question)
    
    return query_knowledge_base


def create_feature_tool(context: AgentDataContext):
    """
    Create a feature lookup tool for an agent.
    
    Args:
        context: Agent data context
        
    Returns:
        Tool function for feature lookups
    """
    def get_entity_features(entity_id: str, entity_type: str = "user") -> str:
        """
        Get features for an entity.
        
        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (user, item, etc.)
            
        Returns:
            Formatted feature values
        """
        entity_key = {f"{entity_type}_id": entity_id}
        features = context.get_features(entity_key)
        
        if not features:
            return f"No features found for {entity_type} {entity_id}"
        
        output = [f"Features for {entity_type} {entity_id}:"]
        for name, value in features.items():
            output.append(f"  - {name}: {value}")
        
        return "\n".join(output)
    
    return get_entity_features
