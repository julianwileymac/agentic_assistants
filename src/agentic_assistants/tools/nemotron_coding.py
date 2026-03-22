"""
Nemotron coding tool integration.

Wraps the served nemotron model as a tool usable by CrewAI agents,
LangChain chains, and the framework's built-in coding assistant.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class NemotronToolConfig(BaseModel):
    """Configuration for the nemotron coding tool."""
    endpoint_url: str = Field(default="http://localhost:11434")
    model_name: str = Field(default="nemotron-nano-coding")
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4096)
    timeout: int = Field(default=120)


class NemotronCodingTool:
    """
    Tool that exposes the nemotron model for coding tasks.

    Can be used standalone, with CrewAI as a tool, or integrated
    with the FrameworkAssistantAgent's coding helper module.

    Example:
        >>> tool = NemotronCodingTool()
        >>> code = tool.generate_code("binary search in Python", language="python")
        >>> review = tool.review_code(code, language="python")
    """

    def __init__(self, config: Optional[NemotronToolConfig] = None):
        self.config = config or NemotronToolConfig()

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> str:
        """Generate code from a natural language description."""
        system = (
            f"You are an expert {language} programmer. Generate clean, "
            "well-documented, production-quality code."
        )
        user_prompt = f"Generate {language} code: {prompt}"
        if context:
            user_prompt = f"Context:\n{context}\n\n{user_prompt}"
        return self._chat(system, user_prompt)

    def review_code(self, code: str, language: str = "python") -> str:
        """Review code for issues, improvements, and best practices."""
        system = "You are an expert code reviewer. Provide thorough, constructive feedback."
        user_prompt = (
            f"Review this {language} code:\n\n```{language}\n{code}\n```\n\n"
            "Identify bugs, security issues, performance problems, and style improvements."
        )
        return self._chat(system, user_prompt)

    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain what a piece of code does."""
        system = "You explain code clearly and thoroughly."
        user_prompt = (
            f"Explain this {language} code:\n\n```{language}\n{code}\n```"
        )
        return self._chat(system, user_prompt)

    def suggest_fix(
        self,
        code: str,
        error: str,
        language: str = "python",
    ) -> str:
        """Suggest a fix for buggy code given an error message."""
        system = "You are a debugging expert. Identify root causes and provide fixes."
        user_prompt = (
            f"Fix this {language} code:\n\n```{language}\n{code}\n```\n\n"
            f"Error: {error}\n\n"
            "Provide the corrected code and explain the fix."
        )
        return self._chat(system, user_prompt)

    def complete_code(
        self,
        code_prefix: str,
        language: str = "python",
    ) -> str:
        """Complete a partial code snippet."""
        system = "Complete the following code naturally and correctly."
        return self._chat(system, code_prefix)

    def _chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat request to the nemotron endpoint."""
        try:
            import httpx
            response = httpx.post(
                f"{self.config.endpoint_url}/api/chat",
                json={
                    "model": self.config.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    },
                },
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Nemotron tool request failed: {e}")
            return f"Error: {e}"

    def as_langchain_tool(self):
        """Return a LangChain-compatible tool wrapper."""
        try:
            from langchain.tools import Tool

            return Tool(
                name="nemotron_coding",
                description=(
                    "Generate, review, explain, or fix code using a fine-tuned "
                    "Nemotron model specialized for coding assistance."
                ),
                func=lambda query: self.generate_code(query),
            )
        except ImportError:
            logger.warning("langchain not installed; cannot create LangChain tool")
            return None

    def as_crewai_tool(self):
        """Return a CrewAI-compatible tool wrapper."""
        try:
            from crewai.tools import BaseTool as CrewAIBaseTool

            tool_instance = self

            class NemotronCrewTool(CrewAIBaseTool):
                name: str = "nemotron_coding"
                description: str = (
                    "Generate, review, explain, or fix code using a fine-tuned "
                    "Nemotron model specialized for coding assistance."
                )

                def _run(self, query: str) -> str:
                    return tool_instance.generate_code(query)

            return NemotronCrewTool()
        except ImportError:
            logger.warning("crewai not installed; cannot create CrewAI tool")
            return None
