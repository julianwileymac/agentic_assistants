"""
Nemotron Coding Agent.

Uses the fine-tuned nemotron model for code generation, review,
debugging, and explanation with RAG context from the knowledge base.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CodingResponse:
    """Response from the coding agent."""
    content: str
    language: str = ""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class NemotronCodingAgent:
    """
    Code generation and assistance using the fine-tuned nemotron model.

    Supports code generation, review, debugging, refactoring, and explanation
    with optional RAG context from indexed code and documentation.

    Example:
        >>> agent = NemotronCodingAgent(config={...}, model_manager=mgr, knowledge_base=kb)
        >>> response = agent.generate_code("Write a binary search in Python")
        >>> print(response.content)
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an expert coding assistant powered by a fine-tuned Nemotron model. "
        "You excel at code generation, code review, debugging, and explaining code. "
        "Provide accurate, well-documented, and idiomatic code. "
        "Always consider edge cases, error handling, and performance."
    )

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_manager: Optional[Any] = None,
        knowledge_base: Optional[Any] = None,
    ):
        self.config = config or {}
        self.model_manager = model_manager
        self.knowledge_base = knowledge_base
        self.system_prompt = self.config.get("system_prompt", self.DEFAULT_SYSTEM_PROMPT)
        self.llm_config = self.config.get("llm", {})

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
        use_rag: bool = True,
        top_k: int = 5,
    ) -> CodingResponse:
        """Generate code from a natural language prompt."""
        context_parts = []
        sources = []

        if use_rag and self.knowledge_base:
            try:
                results = self.knowledge_base.search(
                    query=prompt, collection="codebase", limit=top_k,
                )
                for r in results:
                    context_parts.append(
                        f"Reference: {r.get('source', 'unknown')}\n```\n{r.get('content', '')[:800]}\n```"
                    )
                    sources.append({"file": r.get("source"), "type": "rag"})
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")

        if context:
            context_parts.append(context)

        full_prompt = (
            f"Generate {language} code for the following request.\n\n"
            f"Request: {prompt}"
        )
        if context_parts:
            full_prompt = "\n\n".join(context_parts) + "\n\n" + full_prompt

        response_text = self._call_llm(full_prompt)
        return CodingResponse(
            content=response_text, language=language,
            sources=sources, metadata={"prompt_length": len(full_prompt)},
        )

    def review_code(
        self,
        code: str,
        language: str = "python",
        focus: Optional[List[str]] = None,
    ) -> CodingResponse:
        """Review code for issues and improvements."""
        focus_areas = focus or ["correctness", "performance", "readability", "security"]
        prompt = (
            f"Review this {language} code. Focus on: {', '.join(focus_areas)}\n\n"
            f"```{language}\n{code}\n```\n\n"
            "Provide specific findings with severity, description, and suggested fixes."
        )
        return CodingResponse(
            content=self._call_llm(prompt), language=language,
            metadata={"focus": focus_areas},
        )

    def debug_code(
        self,
        code: str,
        error_message: Optional[str] = None,
        language: str = "python",
    ) -> CodingResponse:
        """Diagnose and fix bugs in code."""
        error_ctx = f"\nError: {error_message}" if error_message else ""
        prompt = (
            f"Debug this {language} code:{error_ctx}\n\n"
            f"```{language}\n{code}\n```\n\n"
            "1. Identify the root cause\n2. Explain the issue\n"
            "3. Provide the corrected code\n4. Suggest preventive measures"
        )
        return CodingResponse(content=self._call_llm(prompt), language=language)

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> CodingResponse:
        """Explain what a piece of code does."""
        prompt = (
            f"Explain this {language} code at a {detail_level} level of detail:\n\n"
            f"```{language}\n{code}\n```"
        )
        return CodingResponse(content=self._call_llm(prompt), language=language)

    def refactor_code(
        self,
        code: str,
        language: str = "python",
        goals: Optional[List[str]] = None,
    ) -> CodingResponse:
        """Suggest refactoring improvements."""
        goals = goals or ["readability", "maintainability"]
        prompt = (
            f"Refactor this {language} code to improve: {', '.join(goals)}\n\n"
            f"```{language}\n{code}\n```\n\n"
            "Show the refactored code and explain each change."
        )
        return CodingResponse(
            content=self._call_llm(prompt), language=language,
            metadata={"goals": goals},
        )

    def _call_llm(self, prompt: str) -> str:
        """Send a prompt to the nemotron model."""
        model = self.llm_config.get("model", "nemotron-nano-coding")
        temperature = self.llm_config.get("temperature", 0.2)

        try:
            if self.model_manager and hasattr(self.model_manager, "chat"):
                return self.model_manager.chat(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    model=model,
                    temperature=temperature,
                )

            import httpx
            ollama_url = "http://localhost:11434"
            response = httpx.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {"temperature": temperature},
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: {e}"
