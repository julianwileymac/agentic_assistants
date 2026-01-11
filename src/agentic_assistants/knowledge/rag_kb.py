"""
RAG-enabled knowledge base implementation.
"""

from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.knowledge.base import (
    KnowledgeBase,
    KnowledgeBaseConfig,
    SearchResult,
)
from agentic_assistants.knowledge.vector_kb import VectorKnowledgeBase
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class RAGKnowledgeBase(KnowledgeBase):
    """
    Knowledge base with RAG (Retrieval-Augmented Generation) support.
    
    Combines vector search with LLM generation for question answering.
    
    Example:
        >>> kb = RAGKnowledgeBase(KnowledgeBaseConfig(name="docs"))
        >>> kb.add_documents(["Python is a programming language..."])
        >>> answer = kb.query("What is Python?")
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer. If the context doesn't contain enough information, say so.
Be concise and accurate."""
    
    DEFAULT_QUERY_TEMPLATE = """Context:
{context}

Question: {question}

Answer:"""
    
    def __init__(
        self,
        config: Optional[KnowledgeBaseConfig] = None,
        llm_fn: Optional[Callable] = None,
    ):
        """
        Initialize RAG knowledge base.
        
        Args:
            config: Knowledge base configuration
            llm_fn: Custom LLM function (optional)
        """
        config = config or KnowledgeBaseConfig()
        super().__init__(config)
        
        # Use vector KB for retrieval
        self._vector_kb = VectorKnowledgeBase(config)
        self._llm_fn = llm_fn
        
        # Customizable prompts
        self.system_prompt = self.DEFAULT_SYSTEM_PROMPT
        self.query_template = self.DEFAULT_QUERY_TEMPLATE
    
    @property
    def llm_fn(self) -> Callable:
        """Get or create LLM function."""
        if self._llm_fn is None:
            self._llm_fn = self._create_default_llm()
        return self._llm_fn
    
    def _create_default_llm(self) -> Callable:
        """Create default LLM function using Ollama."""
        def ollama_generate(prompt: str) -> str:
            try:
                import httpx
                
                response = httpx.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.config.llm_model,
                        "prompt": prompt,
                        "system": self.system_prompt,
                        "stream": False,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                
                return response.json().get("response", "")
                
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return f"Error generating response: {e}"
        
        return ollama_generate
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search the knowledge base."""
        return self._vector_kb.search(query, top_k, filters)
    
    def query(
        self,
        question: str,
        context_docs: Optional[int] = None,
    ) -> str:
        """Query the knowledge base with RAG generation."""
        k = context_docs or self.config.top_k
        
        # Retrieve relevant documents
        results = self.search(question, top_k=k)
        
        if not results:
            return "I couldn't find any relevant information to answer your question."
        
        # Build context
        context = self._build_context(results)
        
        # Generate prompt
        prompt = self.query_template.format(
            context=context,
            question=question,
        )
        
        # Truncate if too long
        if len(prompt) > self.config.max_context_length:
            # Truncate context
            available_length = self.config.max_context_length - len(question) - 100
            context = context[:available_length] + "..."
            prompt = self.query_template.format(
                context=context,
                question=question,
            )
        
        # Generate answer
        answer = self.llm_fn(prompt)
        
        return answer
    
    def _build_context(self, results: List[SearchResult]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            source = result.source or f"Source {i}"
            context_parts.append(f"[{source}]\n{result.content}")
        
        return "\n\n".join(context_parts)
    
    def query_with_sources(
        self,
        question: str,
        context_docs: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Query and return answer with source information."""
        k = context_docs or self.config.top_k
        
        results = self.search(question, top_k=k)
        
        if not results:
            return {
                "answer": "I couldn't find any relevant information.",
                "sources": [],
                "context_used": 0,
            }
        
        context = self._build_context(results)
        prompt = self.query_template.format(
            context=context,
            question=question,
        )
        
        answer = self.llm_fn(prompt)
        
        return {
            "answer": answer,
            "sources": [
                {
                    "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "source": r.source,
                    "score": r.score,
                }
                for r in results
            ],
            "context_used": len(results),
        }
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """Add documents to the knowledge base."""
        return self._vector_kb.add_documents(documents, metadatas, ids)
    
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Delete documents from the knowledge base."""
        return self._vector_kb.delete_documents(ids, filters)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        return self._vector_kb.get_document(doc_id)
    
    def set_prompts(
        self,
        system_prompt: Optional[str] = None,
        query_template: Optional[str] = None,
    ) -> None:
        """
        Customize the prompts used for generation.
        
        Args:
            system_prompt: System prompt for the LLM
            query_template: Template with {context} and {question} placeholders
        """
        if system_prompt:
            self.system_prompt = system_prompt
        if query_template:
            self.query_template = query_template
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        vector_stats = self._vector_kb.get_stats()
        
        return {
            **vector_stats,
            "type": "rag",
            "llm_model": self.config.llm_model,
            "max_context_length": self.config.max_context_length,
        }
