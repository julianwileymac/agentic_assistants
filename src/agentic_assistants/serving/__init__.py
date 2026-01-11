"""
Model serving module.

This module provides model serving and deployment capabilities for:
- Ollama (local LLM serving)
- vLLM (high-throughput serving)
- TGI (Text Generation Inference)

Example:
    >>> from agentic_assistants.serving import ServingManager, OllamaBackend
    >>> 
    >>> manager = ServingManager()
    >>> ollama = manager.get_backend("ollama")
    >>> 
    >>> # Deploy a custom model
    >>> result = await ollama.deploy_model(
    ...     model_path="./outputs/my-model",
    ...     model_name="my-custom-llama",
    ... )
"""

from agentic_assistants.serving.config import (
    ServingConfig,
    EndpointConfig,
    OllamaConfig,
    VLLMConfig,
    TGIConfig,
)
from agentic_assistants.serving.manager import ServingManager

__all__ = [
    "ServingConfig",
    "EndpointConfig",
    "OllamaConfig",
    "VLLMConfig",
    "TGIConfig",
    "ServingManager",
]
