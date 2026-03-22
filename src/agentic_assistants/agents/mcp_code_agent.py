"""
MCP-backed coding agent with provider-agnostic responses.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

import httpx

from agentic_assistants.config import AgenticConfig
from agentic_assistants.llms import LLMProvider
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are a senior software engineer. Use the provided code context to "
    "answer questions precisely. Cite file paths when relevant. If context is "
    "insufficient, say so and suggest where to look next."
)


class McpOllamaCodingAgent:
    """Coding agent that retrieves context via MCP and responds via configurable LLM provider."""

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        mcp_url: Optional[str] = None,
        collection: str = "default",
        top_k: int = 5,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        endpoint: Optional[str] = None,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.config = config or AgenticConfig()
        self.mcp_url = mcp_url or f"http://{self.config.server.host}:{self.config.server.port}/mcp"
        self.collection = collection
        self.top_k = top_k
        self.model = model or self.config.llm.model or self.config.ollama.default_model
        self.provider = provider or self.config.llm.provider
        self.endpoint = endpoint or self.config.assistant.endpoint
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.timeout = timeout
        self._llm_provider = LLMProvider.from_config(
            self.config,
            provider=self.provider,
            model=self.model,
            endpoint=self.endpoint,
            api_key_env=self.config.assistant.openai_api_key_env,
        )

    def _mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        response = httpx.post(self.mcp_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "MCP error"))
        return data.get("result", {})

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search codebase via MCP tools."""
        result = self._mcp_request(
            "tools/call",
            {
                "name": "search_codebase",
                "arguments": {
                    "query": query,
                    "collection": self.collection,
                    "top_k": self.top_k,
                },
            },
        )

        content_blocks = result.get("content", [])
        if not content_blocks:
            return []
        try:
            payload = json.loads(content_blocks[0].get("text", "{}"))
        except json.JSONDecodeError:
            return []
        return payload.get("results", [])

    def answer(self, question: str) -> str:
        """Answer a question using MCP retrieval + Ollama generation."""
        try:
            results = self.search(question)
        except Exception as exc:
            logger.warning("MCP search failed: %s", exc)
            results = []

        context = ""
        if results:
            parts = []
            for idx, item in enumerate(results, start=1):
                snippet = item.get("content", "")
                path = item.get("file_path", "unknown")
                parts.append(f"[{idx}] {path}\n{snippet}")
            context = "\n\n".join(parts)

        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Context:\n{context if context else 'No relevant context found.'}\n\n"
            "Answer:"
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._llm_provider.chat(messages=messages, model=self.model)
        return response.content
