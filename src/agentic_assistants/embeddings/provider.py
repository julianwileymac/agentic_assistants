"""
Embedding provider abstraction for parameterized embeddings.

This module provides a unified interface for different embedding backends:
- Ollama (local, privacy-preserving)
- Sentence Transformers (local, fast)
- OpenAI (cloud, high quality)

Example:
    >>> from agentic_assistants.embeddings import EmbeddingProvider
    >>> 
    >>> # Auto-select based on config
    >>> provider = EmbeddingProvider.from_config()
    >>> 
    >>> # Or specify explicitly
    >>> provider = EmbeddingProvider.create("ollama", model="nomic-embed-text")
    >>> embedding = provider.embed("Search query")
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmbeddingResult:
    """
    Result from an embedding operation.
    
    Attributes:
        embedding: The embedding vector
        model: Model used to generate embedding
        dimension: Embedding dimension
        duration_ms: Time taken in milliseconds
        token_count: Number of tokens (if available)
    """
    
    embedding: list[float]
    model: str
    dimension: int
    duration_ms: float = 0.0
    token_count: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "embedding": self.embedding,
            "model": self.model,
            "dimension": self.dimension,
            "duration_ms": self.duration_ms,
            "token_count": self.token_count,
        }


@dataclass
class BatchEmbeddingResult:
    """
    Result from a batch embedding operation.
    
    Attributes:
        embeddings: List of embedding vectors
        model: Model used
        dimension: Embedding dimension
        duration_ms: Total time taken
        count: Number of embeddings
    """
    
    embeddings: list[list[float]]
    model: str
    dimension: int
    duration_ms: float = 0.0
    count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "embeddings": self.embeddings,
            "model": self.model,
            "dimension": self.dimension,
            "duration_ms": self.duration_ms,
            "count": self.count,
        }


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    
    This class defines the interface that all embedding providers
    must implement, enabling seamless switching between backends.
    
    Attributes:
        model: Model name/identifier
        dimension: Embedding dimension
        config: Configuration instance
    """
    
    # Registry of available providers
    _providers: dict[str, type["EmbeddingProvider"]] = {}
    
    # Default dimensions for common models
    DEFAULT_DIMENSIONS = {
        # Ollama models
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "all-minilm": 384,
        # Sentence Transformers
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "paraphrase-MiniLM-L6-v2": 384,
        # OpenAI
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(
        self,
        model: str,
        dimension: Optional[int] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the embedding provider.
        
        Args:
            model: Model name
            dimension: Embedding dimension (auto-detected if None)
            config: Configuration instance
        """
        self.model = model
        self.config = config or AgenticConfig()
        self.dimension = dimension or self._get_default_dimension(model)
    
    def _get_default_dimension(self, model: str) -> int:
        """Get default dimension for a model."""
        # Check exact match
        if model in self.DEFAULT_DIMENSIONS:
            return self.DEFAULT_DIMENSIONS[model]
        
        # Check partial match
        model_lower = model.lower()
        for name, dim in self.DEFAULT_DIMENSIONS.items():
            if name.lower() in model_lower or model_lower in name.lower():
                return dim
        
        # Default
        return 768
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type["EmbeddingProvider"]) -> None:
        """Register a provider class."""
        cls._providers[name] = provider_class
    
    @classmethod
    def create(
        cls,
        provider: str,
        model: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ) -> "EmbeddingProvider":
        """
        Factory method to create an embedding provider.
        
        Args:
            provider: Provider name ("ollama", "sentence_transformers", "openai")
            model: Model name
            config: Configuration instance
            **kwargs: Additional provider-specific arguments
        
        Returns:
            EmbeddingProvider instance
        
        Raises:
            ValueError: If provider is not supported
        """
        config = config or AgenticConfig()
        
        # Determine model based on provider if not specified
        if model is None:
            if provider == "ollama":
                model = config.vectordb.embedding_model
            elif provider == "sentence_transformers":
                model = "all-MiniLM-L6-v2"
            elif provider == "openai":
                model = "text-embedding-3-small"
            else:
                model = config.vectordb.embedding_model
        
        # Get or lazy-load provider class
        if provider not in cls._providers:
            if provider == "ollama":
                cls._providers["ollama"] = OllamaEmbeddingProvider
            elif provider == "sentence_transformers":
                cls._providers["sentence_transformers"] = SentenceTransformerProvider
            elif provider == "openai":
                cls._providers["openai"] = OpenAIEmbeddingProvider
            else:
                available = ", ".join(cls._providers.keys())
                raise ValueError(
                    f"Unknown embedding provider: {provider}. "
                    f"Available: ollama, sentence_transformers, openai. "
                    f"Registered: {available}"
                )
        
        return cls._providers[provider](model=model, config=config, **kwargs)
    
    @classmethod
    def from_config(cls, config: Optional[AgenticConfig] = None) -> "EmbeddingProvider":
        """
        Create provider from configuration.
        
        Uses config.vectordb.embedding_provider and config.vectordb.embedding_model.
        
        Args:
            config: Configuration instance
        
        Returns:
            Configured EmbeddingProvider
        """
        config = config or AgenticConfig()
        
        # Get provider from config (default to ollama)
        provider = getattr(config.vectordb, "embedding_provider", "ollama")
        model = config.vectordb.embedding_model
        dimension = config.vectordb.embedding_dimension
        
        return cls.create(
            provider=provider,
            model=model,
            config=config,
            dimension=dimension,
        )
    
    @abstractmethod
    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text (implementation)."""
        pass
    
    @abstractmethod
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (implementation)."""
        pass
    
    @trace_function(attributes={"component": "embedding_provider"})
    def embed(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            EmbeddingResult with embedding vector
        """
        start_time = time.time()
        embedding = self._embed(text)
        duration_ms = (time.time() - start_time) * 1000
        
        return EmbeddingResult(
            embedding=embedding,
            model=self.model,
            dimension=len(embedding),
            duration_ms=duration_ms,
        )
    
    @trace_function(attributes={"component": "embedding_provider"})
    def embed_batch(self, texts: list[str]) -> BatchEmbeddingResult:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            BatchEmbeddingResult with embedding vectors
        """
        if not texts:
            return BatchEmbeddingResult(
                embeddings=[],
                model=self.model,
                dimension=self.dimension,
                count=0,
            )
        
        start_time = time.time()
        embeddings = self._embed_batch(texts)
        duration_ms = (time.time() - start_time) * 1000
        
        return BatchEmbeddingResult(
            embeddings=embeddings,
            model=self.model,
            dimension=len(embeddings[0]) if embeddings else self.dimension,
            duration_ms=duration_ms,
            count=len(embeddings),
        )
    
    def embed_raw(self, text: str) -> list[float]:
        """
        Generate embedding and return just the vector.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        return self._embed(text)
    
    def get_info(self) -> dict:
        """Get provider information."""
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
            "dimension": self.dimension,
        }


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Ollama-based embedding provider.
    
    Uses Ollama's embedding API for local, privacy-preserving embeddings.
    
    Supported models:
    - nomic-embed-text (768 dimensions)
    - mxbai-embed-large (1024 dimensions)
    - all-minilm (384 dimensions)
    """
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        config: Optional[AgenticConfig] = None,
        host: Optional[str] = None,
        timeout: int = 60,
        **kwargs,
    ):
        """
        Initialize Ollama embedding provider.
        
        Args:
            model: Ollama embedding model name
            config: Configuration instance
            host: Ollama host URL (uses config if None)
            timeout: Request timeout in seconds
        """
        super().__init__(model=model, config=config, **kwargs)
        self.host = host or self.config.ollama.host
        self.timeout = timeout
    
    def _embed(self, text: str) -> list[float]:
        """Generate embedding using Ollama."""
        import httpx
        
        try:
            response = httpx.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()["embedding"]
            
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for batch using Ollama."""
        # Ollama doesn't have native batch support, so we process sequentially
        # In the future, this could be parallelized
        return [self._embed(text) for text in texts]


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Sentence Transformers embedding provider.
    
    Uses the sentence-transformers library for fast, local embeddings.
    
    Supported models:
    - all-MiniLM-L6-v2 (384 dimensions, fast)
    - all-mpnet-base-v2 (768 dimensions, better quality)
    - paraphrase-MiniLM-L6-v2 (384 dimensions)
    """
    
    def __init__(
        self,
        model: str = "all-MiniLM-L6-v2",
        config: Optional[AgenticConfig] = None,
        device: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Sentence Transformer provider.
        
        Args:
            model: Model name from HuggingFace
            config: Configuration instance
            device: Device to use ("cpu", "cuda", "mps")
        """
        super().__init__(model=model, config=config, **kwargs)
        self.device = device
        self._model = None
    
    @property
    def transformer_model(self):
        """Lazy-load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                
                self._model = SentenceTransformer(self.model, device=self.device)
                logger.info(f"Loaded Sentence Transformer: {self.model}")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    def _embed(self, text: str) -> list[float]:
        """Generate embedding using Sentence Transformers."""
        embedding = self.transformer_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for batch."""
        embeddings = self.transformer_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider.
    
    Uses OpenAI's embedding API for high-quality embeddings.
    Requires OPENAI_API_KEY environment variable.
    
    Supported models:
    - text-embedding-3-small (1536 dimensions)
    - text-embedding-3-large (3072 dimensions)
    - text-embedding-ada-002 (1536 dimensions)
    """
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        config: Optional[AgenticConfig] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize OpenAI embedding provider.
        
        Args:
            model: OpenAI embedding model name
            config: Configuration instance
            api_key: OpenAI API key (uses env var if None)
        """
        super().__init__(model=model, config=config, **kwargs)
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                import os
                
                api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OpenAI API key not found. "
                        "Set OPENAI_API_KEY environment variable or pass api_key parameter."
                    )
                
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "openai is required. Install with: pip install openai"
                )
        return self._client
    
    def _embed(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding
    
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for batch using OpenAI."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


# Register default providers
EmbeddingProvider.register_provider("ollama", OllamaEmbeddingProvider)
EmbeddingProvider.register_provider("sentence_transformers", SentenceTransformerProvider)
EmbeddingProvider.register_provider("openai", OpenAIEmbeddingProvider)


def get_embedding_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config: Optional[AgenticConfig] = None,
) -> EmbeddingProvider:
    """
    Convenience function to get an embedding provider.
    
    Args:
        provider: Provider name
        model: Model name
        config: Configuration instance
    
    Returns:
        Configured EmbeddingProvider
    
    Example:
        >>> provider = get_embedding_provider("ollama", "nomic-embed-text")
        >>> embedding = provider.embed("Hello world")
    """
    if provider is None:
        return EmbeddingProvider.from_config(config)
    return EmbeddingProvider.create(provider, model, config)

