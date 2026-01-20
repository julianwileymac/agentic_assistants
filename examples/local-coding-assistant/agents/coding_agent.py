"""
Main Coding Agent for the Local Coding Assistant.

Provides intelligent code assistance with memory and caching.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResponse:
    """Response from the coding agent."""
    
    content: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodingAgent:
    """
    Main coding assistant agent.
    
    Combines vector search, memory, and LLM capabilities
    to answer coding questions and assist with development.
    
    Example:
        >>> agent = CodingAgent()
        >>> response = agent.answer("How does authentication work?")
        >>> print(response.content)
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are an expert coding assistant with deep knowledge of software development.
You have access to the user's codebase and can search for relevant code,
explain implementations, suggest improvements, and help debug issues.

Always:
- Cite specific files and line numbers when referencing code
- Explain your reasoning step by step
- Suggest best practices and potential improvements
- Consider edge cases and error handling

When analyzing code:
1. First understand the overall structure and purpose
2. Identify key components and their relationships
3. Look for potential issues or improvements
4. Provide clear, actionable suggestions"""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        memory_enabled: bool = True,
        cache_enabled: bool = True,
        vectordb_collection: str = "codebase",
    ):
        """
        Initialize the coding agent.
        
        Args:
            system_prompt: Custom system prompt
            llm_config: LLM configuration
            memory_enabled: Enable memory features
            cache_enabled: Enable solution caching
            vectordb_collection: Default vector store collection
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm_config = llm_config or {}
        self.memory_enabled = memory_enabled
        self.cache_enabled = cache_enabled
        self.vectordb_collection = vectordb_collection
        
        # Lazy-loaded components
        self._memory = None
        self._episodic = None
        self._cache = None
        self._vectordb = None
    
    @property
    def memory(self):
        """Get memory store."""
        if self._memory is None and self.memory_enabled:
            from agentic_assistants.memory import get_memory_store
            self._memory = get_memory_store(backend="mem0")
        return self._memory
    
    @property
    def episodic(self):
        """Get episodic memory."""
        if self._episodic is None and self.memory_enabled:
            from agentic_assistants.memory import EpisodicMemory
            self._episodic = EpisodicMemory(memory_store=self.memory)
        return self._episodic
    
    @property
    def cache(self):
        """Get solution cache."""
        if self._cache is None and self.cache_enabled:
            from agentic_assistants.cache import get_solution_cache
            self._cache = get_solution_cache()
        return self._cache
    
    @property
    def vectordb(self):
        """Get vector store."""
        if self._vectordb is None:
            from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
            self._vectordb = ScopedVectorStore()
        return self._vectordb
    
    def answer(
        self,
        question: str,
        context: Optional[str] = None,
        search_codebase: bool = True,
        use_memory: bool = True,
        top_k: int = 5,
    ) -> AgentResponse:
        """
        Answer a coding question.
        
        Args:
            question: The question to answer
            context: Additional context
            search_codebase: Search codebase for relevant code
            use_memory: Include relevant memories
            top_k: Number of search results
            
        Returns:
            AgentResponse with answer and sources
        """
        context_parts = []
        sources = []
        
        # Search codebase
        if search_codebase:
            try:
                results = self.vectordb.search(
                    query=question,
                    collection=self.vectordb_collection,
                    top_k=top_k,
                )
                
                for r in results:
                    context_parts.append(
                        f"File: {r.document.metadata.get('source', 'unknown')}\n"
                        f"```\n{r.document.content[:800]}\n```"
                    )
                    sources.append({
                        "file": r.document.metadata.get("source"),
                        "score": r.score,
                        "type": "codebase",
                    })
            except Exception as e:
                logger.warning(f"Codebase search failed: {e}")
        
        # Get relevant memories
        if use_memory and self.memory:
            try:
                memory_context = self.memory.get_relevant_context(
                    query=question,
                    max_memories=3,
                )
                if memory_context:
                    context_parts.append(f"From memory:\n{memory_context}")
                    sources.append({"type": "memory"})
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")
        
        # Add provided context
        if context:
            context_parts.append(context)
        
        # Build full context
        full_context = "\n\n".join(context_parts) if context_parts else ""
        
        # Get LLM response
        response_text = self._call_llm(question, full_context)
        
        # Record interaction
        if self.episodic:
            try:
                self.episodic.record_conversation(
                    user_message=question,
                    assistant_response=response_text,
                    context={"sources": len(sources)},
                )
            except Exception as e:
                logger.warning(f"Failed to record interaction: {e}")
        
        return AgentResponse(
            content=response_text,
            sources=sources,
            metadata={"context_length": len(full_context)},
        )
    
    def _call_llm(self, question: str, context: str) -> str:
        """Call the LLM with the question and context."""
        provider = self.llm_config.get("provider", "ollama")
        
        try:
            if provider == "ollama":
                import ollama
                response = ollama.chat(
                    model=self.llm_config.get("model", "llama3.2"),
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"{context}\n\nQuestion: {question}"},
                    ],
                )
                return response["message"]["content"]
            
            elif provider == "openai":
                import openai
                client = openai.OpenAI(api_key=self.llm_config.get("api_key"))
                response = client.chat.completions.create(
                    model=self.llm_config.get("model", "gpt-4-turbo-preview"),
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"{context}\n\nQuestion: {question}"},
                    ],
                )
                return response.choices[0].message.content
            
            else:
                return f"LLM provider '{provider}' not supported"
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: {e}"
    
    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> AgentResponse:
        """
        Explain a piece of code.
        
        Args:
            code: Code to explain
            language: Programming language
            detail_level: low, medium, or high
            
        Returns:
            AgentResponse with explanation
        """
        prompt = f"""Explain the following {language} code at a {detail_level} level of detail:

```{language}
{code}
```

Provide:
1. A brief summary of what the code does
2. Explanation of key components
3. Any potential issues or improvements"""
        
        return self.answer(prompt, search_codebase=False, use_memory=False)
    
    def suggest_improvements(
        self,
        code: str,
        language: str = "python",
        focus: Optional[List[str]] = None,
    ) -> AgentResponse:
        """
        Suggest improvements for code.
        
        Args:
            code: Code to analyze
            language: Programming language
            focus: Areas to focus on (performance, readability, security, etc.)
            
        Returns:
            AgentResponse with suggestions
        """
        focus_areas = focus or ["readability", "performance", "best practices"]
        focus_str = ", ".join(focus_areas)
        
        prompt = f"""Review this {language} code and suggest improvements focused on: {focus_str}

```{language}
{code}
```

For each suggestion:
1. Explain the issue
2. Provide the improved code
3. Explain why it's better"""
        
        return self.answer(prompt, search_codebase=False, use_memory=False)
    
    def debug_code(
        self,
        code: str,
        error_message: Optional[str] = None,
        language: str = "python",
    ) -> AgentResponse:
        """
        Help debug code.
        
        Args:
            code: Code with the bug
            error_message: Error message if available
            language: Programming language
            
        Returns:
            AgentResponse with debugging help
        """
        error_context = f"\nError message: {error_message}" if error_message else ""
        
        prompt = f"""Debug this {language} code:{error_context}

```{language}
{code}
```

Please:
1. Identify the likely cause of the issue
2. Explain what's going wrong
3. Provide the corrected code
4. Suggest how to prevent similar issues"""
        
        response = self.answer(prompt, search_codebase=True, use_memory=True)
        
        # Record as error for learning
        if self.episodic:
            try:
                self.episodic.record_error(
                    error_description=error_message or "Unknown error",
                    context={"code_sample": code[:200]},
                    resolution=response.content[:500],
                )
            except Exception as e:
                logger.warning(f"Failed to record error: {e}")
        
        return response
