"""
Coding Helper Module for the Framework Assistant.

This module provides code-related assistance including:
- Code generation with RAG context from project codebase
- Code review and analysis
- Debugging assistance
- Refactoring suggestions

Example:
    >>> helper = CodingHelperModule(config, knowledge_base)
    >>> code = helper.generate_code("Create a function to sort a list")
    >>> review = helper.review_code(existing_code)
"""

import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.knowledge import KnowledgeBase
    from agentic_assistants.memory import AgentMemory
    from agentic_assistants.observability import UsageTracker

logger = get_logger(__name__)


class CodingHelperModule:
    """
    Provides coding assistance capabilities.
    
    Features:
    - Code generation with RAG-enhanced context
    - Code review and quality analysis
    - Bug detection and debugging help
    - Refactoring suggestions
    - Code explanation
    
    Attributes:
        config: Framework configuration
        knowledge_base: Optional RAG knowledge base for code context
        memory: Optional memory store for conversation history
        usage_tracker: Optional usage tracker for analytics
    """
    
    DEFAULT_CODE_SYSTEM_PROMPT = """You are an expert software developer assistant. 
You help with coding tasks including:
- Writing clean, efficient code
- Reviewing code for bugs and improvements
- Debugging issues
- Explaining code
- Suggesting refactorings

Always provide well-structured, documented code. Follow best practices for the language being used.
When reviewing code, be constructive and specific about issues and improvements."""

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        knowledge_base: Optional["KnowledgeBase"] = None,
        memory: Optional["AgentMemory"] = None,
        usage_tracker: Optional["UsageTracker"] = None,
    ):
        """
        Initialize the coding helper module.
        
        Args:
            config: Configuration instance
            knowledge_base: RAG knowledge base for code context
            memory: Memory store for conversation history
            usage_tracker: Usage tracker for analytics
        """
        self.config = config or AgenticConfig()
        self.knowledge_base = knowledge_base
        self.memory = memory
        self.usage_tracker = usage_tracker
        self._conversation_history: List[Dict[str, str]] = []
    
    def _get_model(self) -> str:
        """Get the model to use for code generation."""
        return self.config.assistant.model or self.config.ollama.default_model
    
    def _call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Make an LLM call."""
        import httpx
        
        system = system_message or self.DEFAULT_CODE_SYSTEM_PROMPT
        
        messages = [{"role": "system", "content": system}]
        messages.extend(self._conversation_history[-10:])  # Last 10 messages
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        response = httpx.post(
            f"{self.config.ollama.host}/api/chat",
            json={
                "model": self._get_model(),
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=self.config.ollama.timeout,
        )
        response.raise_for_status()
        
        duration_ms = (time.time() - start_time) * 1000
        result = response.json()
        content = result.get("message", {}).get("content", "")
        
        # Update conversation history
        self._conversation_history.append({"role": "user", "content": prompt})
        self._conversation_history.append({"role": "assistant", "content": content})
        
        # Track usage
        if self.usage_tracker:
            self.usage_tracker.track_model_inference(
                model=self._get_model(),
                duration_ms=duration_ms,
                prompt_tokens=result.get("prompt_eval_count", 0),
                completion_tokens=result.get("eval_count", 0),
            )
        
        return content
    
    def _get_code_context(self, query: str, top_k: int = 5) -> str:
        """Get relevant code context from the knowledge base."""
        if not self.knowledge_base:
            return ""
        
        try:
            start_time = time.time()
            results = self.knowledge_base.search(query, top_k=top_k)
            duration_ms = (time.time() - start_time) * 1000
            
            if not results:
                return ""
            
            # Track RAG query
            if self.usage_tracker:
                self.usage_tracker.track_rag_query(
                    knowledge_base=getattr(self.knowledge_base, 'name', 'code_kb'),
                    query=query[:200],
                    num_results=len(results),
                    duration_ms=duration_ms,
                    top_score=results[0].score if results else None,
                    avg_score=sum(r.score for r in results) / len(results) if results else None,
                    used_for_generation=True,
                )
            
            context_parts = []
            for r in results:
                source = r.source or "Unknown"
                context_parts.append(f"### {source}\n```\n{r.content}\n```")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Failed to get code context: {e}")
            return ""
    
    def generate_code(
        self,
        request: str,
        language: Optional[str] = None,
        use_rag: bool = True,
        additional_context: Optional[str] = None,
    ) -> str:
        """
        Generate code based on a request.
        
        Args:
            request: Description of what code to generate
            language: Programming language (optional, will be inferred)
            use_rag: Whether to use RAG context
            additional_context: Additional context to include
            
        Returns:
            Generated code
        """
        # Build the prompt
        prompt_parts = [f"Generate code for the following request:\n\n{request}"]
        
        if language:
            prompt_parts.append(f"\nLanguage: {language}")
        
        # Add RAG context if enabled
        if use_rag and self.knowledge_base:
            code_context = self._get_code_context(request)
            if code_context:
                prompt_parts.append(f"\nRelevant code from the codebase for reference:\n{code_context}")
        
        if additional_context:
            prompt_parts.append(f"\nAdditional context:\n{additional_context}")
        
        prompt_parts.append("\nPlease provide well-documented, clean code.")
        
        prompt = "\n".join(prompt_parts)
        
        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="code_generation",
                feature_used="coding_helper",
                input_length=len(request),
            )
        
        return self._call_llm(prompt, temperature=0.3)
    
    def review_code(
        self,
        code: str,
        focus_areas: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Review code and provide feedback.
        
        Args:
            code: The code to review
            focus_areas: Specific areas to focus on (e.g., ["security", "performance"])
            language: Programming language
            
        Returns:
            Review results with issues and suggestions
        """
        focus = focus_areas or ["bugs", "performance", "readability", "best practices"]
        
        prompt = f"""Review the following code and provide detailed feedback.

Code to review:
```{language or ''}
{code}
```

Focus on these areas:
{', '.join(focus)}

Please provide:
1. Overall assessment
2. Specific issues found (with line references if possible)
3. Suggestions for improvement
4. Security concerns (if any)
5. Performance considerations

Format your response as a structured review."""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="code_review",
                feature_used="coding_helper",
                input_length=len(code),
            )
        
        review_text = self._call_llm(prompt, temperature=0.2)
        
        return {
            "review": review_text,
            "code_length": len(code),
            "focus_areas": focus,
            "language": language,
        }
    
    def debug_code(
        self,
        code: str,
        error_message: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Help debug code issues.
        
        Args:
            code: The code with the bug
            error_message: Error message if any
            expected_behavior: What the code should do
            actual_behavior: What the code actually does
            
        Returns:
            Debugging analysis and suggested fixes
        """
        prompt_parts = [f"Help debug the following code:\n\n```\n{code}\n```"]
        
        if error_message:
            prompt_parts.append(f"\nError message:\n{error_message}")
        
        if expected_behavior:
            prompt_parts.append(f"\nExpected behavior:\n{expected_behavior}")
        
        if actual_behavior:
            prompt_parts.append(f"\nActual behavior:\n{actual_behavior}")
        
        prompt_parts.append("""
Please provide:
1. Root cause analysis
2. Explanation of what's going wrong
3. Fixed code
4. Prevention tips for similar issues""")
        
        prompt = "\n".join(prompt_parts)
        
        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="debugging",
                feature_used="coding_helper",
                input_length=len(code),
            )
        
        debug_text = self._call_llm(prompt, temperature=0.2)
        
        return {
            "analysis": debug_text,
            "had_error": bool(error_message),
        }
    
    def explain_code(
        self,
        code: str,
        detail_level: str = "medium",
    ) -> str:
        """
        Explain what code does.
        
        Args:
            code: The code to explain
            detail_level: Level of detail (brief, medium, detailed)
            
        Returns:
            Explanation of the code
        """
        detail_instructions = {
            "brief": "Provide a brief, high-level explanation.",
            "medium": "Provide a clear explanation covering the main logic and purpose.",
            "detailed": "Provide a detailed, line-by-line explanation suitable for learning.",
        }
        
        prompt = f"""Explain the following code:

```
{code}
```

{detail_instructions.get(detail_level, detail_instructions['medium'])}

Include:
- What the code does overall
- Key algorithms or patterns used
- Any important considerations"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="code_explanation",
                feature_used="coding_helper",
                input_length=len(code),
            )
        
        return self._call_llm(prompt, temperature=0.3)
    
    def suggest_refactoring(
        self,
        code: str,
        goals: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Suggest refactoring improvements.
        
        Args:
            code: The code to refactor
            goals: Refactoring goals (e.g., ["simplify", "improve_performance"])
            
        Returns:
            Refactoring suggestions and improved code
        """
        goals = goals or ["improve readability", "reduce complexity", "follow best practices"]
        
        prompt = f"""Suggest refactoring improvements for the following code:

```
{code}
```

Refactoring goals:
{', '.join(goals)}

Please provide:
1. Analysis of current code structure
2. Specific refactoring suggestions
3. Refactored code
4. Explanation of changes made"""

        # Track user interaction
        if self.usage_tracker:
            self.usage_tracker.track_user_interaction(
                interaction_type="refactoring",
                feature_used="coding_helper",
                input_length=len(code),
            )
        
        refactor_text = self._call_llm(prompt, temperature=0.3)
        
        return {
            "suggestions": refactor_text,
            "goals": goals,
        }
    
    def complete_code(
        self,
        code: str,
        cursor_position: Optional[int] = None,
    ) -> str:
        """
        Complete code at the given position.
        
        Args:
            code: Partial code
            cursor_position: Position where completion is needed
            
        Returns:
            Code completion suggestion
        """
        if cursor_position is not None:
            before = code[:cursor_position]
            after = code[cursor_position:]
            prompt = f"""Complete the code at the cursor position (marked with <CURSOR>):

{before}<CURSOR>{after}

Provide only the completion, not the full code."""
        else:
            prompt = f"""Complete the following code:

{code}

Provide the completion to make this code functional."""

        return self._call_llm(prompt, temperature=0.2)
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._conversation_history = []
