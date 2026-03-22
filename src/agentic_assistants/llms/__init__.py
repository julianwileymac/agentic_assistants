"""
LLM provider abstraction for chat inference.

This package provides a provider-agnostic interface for chat completions:
- Ollama local HTTP API
- Hugging Face local transformers inference
- OpenAI-compatible HTTP endpoints (OpenAI, vLLM, TGI, etc.)
"""

from agentic_assistants.llms.provider import (
    ChatResult,
    HuggingFaceLocalLLMProvider,
    LLMProvider,
    OllamaLLMProvider,
    OpenAICompatibleLLMProvider,
)

__all__ = [
    "ChatResult",
    "LLMProvider",
    "OllamaLLMProvider",
    "HuggingFaceLocalLLMProvider",
    "OpenAICompatibleLLMProvider",
]

