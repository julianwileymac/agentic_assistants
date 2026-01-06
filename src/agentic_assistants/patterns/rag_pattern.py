"""
RAG (Retrieval-Augmented Generation) Pattern implementation.

This module provides a configurable RAG pattern that:
1. Retrieves relevant context from a vector store
2. Augments the prompt with retrieved context
3. Generates a response using an LLM

Example:
    >>> from agentic_assistants.patterns import RAGPattern
    >>> 
    >>> rag = RAGPattern(
    ...     vector_store=store,
    ...     collection="codebase"
    ... )
    >>> response = rag.query("How does the auth system work?")
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.patterns.base import (
    AgenticPattern,
    PatternConfig,
    PatternResult,
)
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import SearchResult, VectorStore

logger = get_logger(__name__)


@dataclass
class RAGConfig(PatternConfig):
    """
    Configuration for RAG pattern.
    
    Attributes:
        collection: Vector store collection to search
        top_k: Number of documents to retrieve
        min_score: Minimum similarity score threshold
        include_metadata: Include document metadata in context
        context_template: Template for formatting context
        prompt_template: Template for the final prompt
        max_context_length: Maximum context length in characters
    """
    
    name: str = "rag"
    description: str = "Retrieval-Augmented Generation pattern"
    collection: str = "default"
    top_k: int = 5
    min_score: float = 0.0
    include_metadata: bool = True
    context_template: str = "[{index}] {source}:\n{content}"
    prompt_template: str = """Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
    max_context_length: int = 8000


class RAGPattern(AgenticPattern):
    """
    Retrieval-Augmented Generation pattern.
    
    This pattern implements the RAG workflow:
    1. Retrieve: Search vector store for relevant documents
    2. Augment: Format retrieved documents as context
    3. Generate: Send augmented prompt to LLM
    
    Attributes:
        vector_store: Vector store for retrieval
        llm_fn: Function to call LLM
        rag_config: RAG-specific configuration
    
    Example:
        >>> # With Ollama
        >>> rag = RAGPattern(
        ...     vector_store=store,
        ...     llm_fn=ollama.chat,
        ...     collection="docs"
        ... )
        >>> 
        >>> # Query
        >>> result = rag.query("What is the main entry point?")
        >>> print(result.output)
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        llm_fn: Optional[Callable] = None,
        collection: str = "default",
        top_k: int = 5,
        config: Optional[AgenticConfig] = None,
        rag_config: Optional[RAGConfig] = None,
    ):
        """
        Initialize the RAG pattern.
        
        Args:
            vector_store: Vector store for retrieval
            llm_fn: Function to generate responses (optional)
            collection: Default collection to search
            top_k: Default number of results
            config: Framework configuration
            rag_config: RAG configuration
        """
        rag_config = rag_config or RAGConfig(
            collection=collection,
            top_k=top_k,
        )
        super().__init__(config=config, pattern_config=rag_config)
        
        self.rag_config = rag_config
        self._vector_store = vector_store
        self._llm_fn = llm_fn
    
    @property
    def vector_store(self) -> VectorStore:
        """Get or create vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore.create(config=self.config)
        return self._vector_store
    
    @property
    def llm_fn(self) -> Callable:
        """Get or create LLM function."""
        if self._llm_fn is None:
            # Default to Ollama
            from agentic_assistants.core.ollama import OllamaManager
            ollama = OllamaManager(self.config)
            self._llm_fn = lambda messages: ollama.chat(messages)["message"]["content"]
        return self._llm_fn
    
    @trace_function(attributes={"pattern": "rag", "step": "retrieve"})
    def retrieve(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: Optional[int] = None,
        filter_metadata: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Retrieve relevant documents.
        
        Args:
            query: Search query
            collection: Collection to search
            top_k: Number of results
            filter_metadata: Metadata filters
        
        Returns:
            List of search results
        """
        start_time = time.time()
        
        results = self.vector_store.search(
            query=query,
            collection=collection or self.rag_config.collection,
            top_k=top_k or self.rag_config.top_k,
            filter_metadata=filter_metadata,
        )
        
        # Filter by minimum score
        if self.rag_config.min_score > 0:
            results = [r for r in results if r.score >= self.rag_config.min_score]
        
        duration_ms = (time.time() - start_time) * 1000
        self.record_step(
            action="retrieve",
            input_data={"query": query, "top_k": top_k or self.rag_config.top_k},
            output_data={"count": len(results)},
            duration_ms=duration_ms,
        )
        
        return results
    
    @trace_function(attributes={"pattern": "rag", "step": "augment"})
    def augment(
        self,
        query: str,
        results: list[SearchResult],
    ) -> str:
        """
        Augment the query with retrieved context.
        
        Args:
            query: Original query
            results: Retrieved results
        
        Returns:
            Augmented prompt
        """
        start_time = time.time()
        
        # Format context from results
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result.document.metadata.get("file_path", "unknown")
            content = result.document.content
            
            formatted = self.rag_config.context_template.format(
                index=i,
                source=source,
                content=content,
                score=result.score,
            )
            context_parts.append(formatted)
        
        context = "\n\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > self.rag_config.max_context_length:
            context = context[:self.rag_config.max_context_length] + "\n...[truncated]"
        
        # Format final prompt
        prompt = self.rag_config.prompt_template.format(
            context=context,
            question=query,
        )
        
        duration_ms = (time.time() - start_time) * 1000
        self.record_step(
            action="augment",
            input_data={"query": query, "context_count": len(results)},
            output_data={"prompt_length": len(prompt)},
            duration_ms=duration_ms,
        )
        
        return prompt
    
    @trace_function(attributes={"pattern": "rag", "step": "generate"})
    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Augmented prompt
        
        Returns:
            Generated response
        """
        start_time = time.time()
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_fn(messages)
        
        duration_ms = (time.time() - start_time) * 1000
        self.record_step(
            action="generate",
            input_data={"prompt_length": len(prompt)},
            output_data={"response_length": len(response)},
            duration_ms=duration_ms,
        )
        
        return response
    
    def _execute(self, input_data: Any) -> Any:
        """Execute the RAG pattern."""
        # Handle different input types
        if isinstance(input_data, str):
            query = input_data
            collection = self.rag_config.collection
        elif isinstance(input_data, dict):
            query = input_data.get("query", input_data.get("question", ""))
            collection = input_data.get("collection", self.rag_config.collection)
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        # Execute RAG pipeline
        results = self.retrieve(query, collection)
        
        if not results:
            logger.warning("No relevant documents found")
            return "No relevant context found to answer the question."
        
        prompt = self.augment(query, results)
        response = self.generate(prompt)
        
        return response
    
    def query(
        self,
        question: str,
        collection: Optional[str] = None,
        experiment_name: Optional[str] = None,
    ) -> PatternResult:
        """
        Convenience method for RAG queries.
        
        Args:
            question: Question to answer
            collection: Collection to search
            experiment_name: MLFlow experiment name
        
        Returns:
            PatternResult with answer
        """
        input_data = {"query": question}
        if collection:
            input_data["collection"] = collection
        
        return self.execute(
            input_data=input_data,
            experiment_name=experiment_name,
            run_name=f"rag-{question[:30]}",
        )
    
    def retrieve_only(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> list[dict]:
        """
        Retrieve without generation.
        
        Args:
            query: Search query
            collection: Collection to search
            top_k: Number of results
        
        Returns:
            List of results as dictionaries
        """
        results = self.retrieve(query, collection, top_k)
        return [
            {
                "content": r.document.content,
                "metadata": r.document.metadata,
                "score": r.score,
            }
            for r in results
        ]

