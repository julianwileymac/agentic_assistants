"""
Provider-agnostic LLM chat abstraction.

Supported providers:
- ollama: local Ollama HTTP API
- huggingface_local: local transformers-based inference
- openai_compatible: any OpenAI-compatible chat endpoint
"""

from __future__ import annotations

import asyncio
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import RLock
from typing import Any, Optional

import httpx

from agentic_assistants.config import AgenticConfig
from agentic_assistants.integrations.huggingface import HuggingFaceHubIntegration
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatResult:
    """Normalized chat response across providers."""

    content: str
    model: str
    provider: str
    duration_ms: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    raw_response: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "duration_ms": self.duration_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "raw_response": self.raw_response,
        }


class LLMProvider(ABC):
    """Base class for provider-specific chat implementations."""

    _providers: dict[str, type["LLMProvider"]] = {}

    def __init__(
        self,
        *,
        model: str,
        config: Optional[AgenticConfig] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.config = config or AgenticConfig()
        self.model = model
        self.timeout = timeout or float(getattr(self.config.ollama, "timeout", 120))

    @classmethod
    def register_provider(cls, name: str, provider_class: type["LLMProvider"]) -> None:
        cls._providers[name] = provider_class

    @classmethod
    def _canonical_provider_name(cls, provider: str) -> str:
        normalized = provider.strip().lower().replace("-", "_")
        alias_map = {
            "openai": "openai_compatible",
            "openai_compat": "openai_compatible",
            "openai_compatible": "openai_compatible",
            "hf_local": "huggingface_local",
            "huggingface": "huggingface_local",
            "huggingface_local": "huggingface_local",
            "ollama": "ollama",
        }
        return alias_map.get(normalized, normalized)

    @classmethod
    def create(
        cls,
        provider: str,
        *,
        model: str,
        config: Optional[AgenticConfig] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> "LLMProvider":
        canonical_provider = cls._canonical_provider_name(provider)
        provider_cls = cls._providers.get(canonical_provider)
        if provider_cls is None:
            available = ", ".join(sorted(cls._providers.keys()))
            raise ValueError(
                f"Unknown LLM provider '{provider}'. "
                f"Available providers: {available}"
            )

        return provider_cls(
            model=model,
            config=config,
            timeout=timeout,
            **kwargs,
        )

    @classmethod
    def from_config(
        cls,
        config: Optional[AgenticConfig] = None,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> "LLMProvider":
        config = config or AgenticConfig()
        llm_cfg = getattr(config, "llm", None)

        provider_name = provider or getattr(llm_cfg, "provider", "ollama")
        provider_name = cls._canonical_provider_name(provider_name)

        default_model = (
            model
            or getattr(llm_cfg, "model", None)
            or getattr(config, "framework_model", None)
            or getattr(config.assistant, "model", None)
            or config.ollama.default_model
        )

        timeout = kwargs.pop("timeout", None) or getattr(llm_cfg, "timeout", None) or config.ollama.timeout
        logger.debug(
            "Resolving LLM provider from configuration",
            extra={
                "provider": provider_name,
                "model": default_model,
                "endpoint_override": endpoint,
                "timeout": timeout,
            },
        )

        if provider_name == "ollama":
            host = (
                endpoint
                or kwargs.pop("host", None)
                or getattr(llm_cfg, "ollama_host", None)
                or config.ollama.host
            )
            return cls.create(
                provider_name,
                model=default_model,
                config=config,
                timeout=timeout,
                host=host,
                **kwargs,
            )

        if provider_name == "openai_compatible":
            base_url = (
                endpoint
                or kwargs.pop("base_url", None)
                or getattr(llm_cfg, "openai_base_url", None)
                or "http://localhost:8000/v1"
            )
            api_key_env = kwargs.pop("api_key_env", None) or getattr(llm_cfg, "openai_api_key_env", "OPENAI_API_KEY")
            resolved_api_key = api_key or kwargs.pop("resolved_api_key", None) or os.getenv(api_key_env) or os.getenv("OPENAI_API_KEY") or "dummy"
            return cls.create(
                provider_name,
                model=default_model,
                config=config,
                timeout=timeout,
                base_url=base_url,
                api_key=resolved_api_key,
                **kwargs,
            )

        if provider_name == "huggingface_local":
            hf_model = (
                model
                or kwargs.pop("hf_model", None)
                or getattr(llm_cfg, "hf_local_model", None)
                or getattr(config.assistant, "model", None)
                or config.ollama.default_model
            )
            return cls.create(
                provider_name,
                model=hf_model,
                config=config,
                timeout=timeout,
                **kwargs,
            )

        return cls.create(
            provider_name,
            model=default_model,
            config=config,
            timeout=timeout,
            **kwargs,
        )

    @staticmethod
    def normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for message in messages:
            role = str(message.get("role", "user")).strip() or "user"
            content = message.get("content", "")
            normalized.append({"role": role, "content": str(content)})
        return normalized

    @abstractmethod
    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Run a synchronous chat completion."""

    async def achat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Run chat completion asynchronously."""

        return await asyncio.to_thread(
            self.chat,
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs,
        )


class OllamaLLMProvider(LLMProvider):
    """LLM provider for Ollama's `/api/chat` endpoint."""

    def __init__(
        self,
        *,
        model: str,
        host: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout)
        self.host = (host or self.config.ollama.host).rstrip("/")
        self._client = httpx.Client(timeout=self.timeout)

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        start = time.time()
        resolved_model = model or self.model
        normalized_messages = self.normalize_messages(messages)

        payload: dict[str, Any] = {
            "model": resolved_model,
            "messages": normalized_messages,
            "stream": False,
        }

        options = kwargs.pop("options", {}) or {}
        if temperature is not None:
            options["temperature"] = temperature
        if options:
            payload["options"] = options
        payload.update(kwargs)

        logger.debug(
            "Dispatching Ollama chat request",
            extra={
                "provider": "ollama",
                "model": resolved_model,
                "endpoint": self.host,
                "message_count": len(normalized_messages),
            },
        )
        try:
            response = self._client.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.error(
                "Ollama chat request failed",
                extra={
                    "provider": "ollama",
                    "model": resolved_model,
                    "endpoint": self.host,
                    "error": str(exc),
                },
            )
            raise

        duration_ms = (time.time() - start) * 1000
        prompt_tokens = data.get("prompt_eval_count")
        completion_tokens = data.get("eval_count")
        total_tokens = None
        if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
            total_tokens = prompt_tokens + completion_tokens

        result = ChatResult(
            content=data.get("message", {}).get("content", ""),
            model=resolved_model,
            provider="ollama",
            duration_ms=duration_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw_response=data,
        )
        logger.info(
            "Ollama chat request completed",
            extra={
                "provider": "ollama",
                "model": resolved_model,
                "endpoint": self.host,
                "duration_ms": duration_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        )
        return result


class OpenAICompatibleLLMProvider(LLMProvider):
    """LLM provider for OpenAI-compatible chat completion endpoints."""

    def __init__(
        self,
        *,
        model: str,
        base_url: str,
        api_key: str,
        config: Optional[AgenticConfig] = None,
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        try:
            from openai import AsyncOpenAI, OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is required for openai_compatible provider. "
                "Install optional dependencies with: poetry install --extras llm-providers"
            ) from exc

        self._sync_client = OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=self.timeout)
        self._async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key, timeout=self.timeout)

    @staticmethod
    def _extract_content(message_content: Any) -> str:
        if isinstance(message_content, str):
            return message_content
        if isinstance(message_content, list):
            parts: list[str] = []
            for item in message_content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(str(text))
            return "\n".join(parts)
        return str(message_content or "")

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        start = time.time()
        resolved_model = model or self.model
        normalized_messages = self.normalize_messages(messages)

        call_kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": normalized_messages,
            **kwargs,
        }
        if temperature is not None:
            call_kwargs["temperature"] = temperature

        logger.debug(
            "Dispatching OpenAI-compatible chat request",
            extra={
                "provider": "openai_compatible",
                "model": resolved_model,
                "endpoint": self.base_url,
                "message_count": len(normalized_messages),
            },
        )
        try:
            response = self._sync_client.chat.completions.create(**call_kwargs)
        except Exception as exc:
            logger.error(
                "OpenAI-compatible chat request failed",
                extra={
                    "provider": "openai_compatible",
                    "model": resolved_model,
                    "endpoint": self.base_url,
                    "error": str(exc),
                },
            )
            raise
        duration_ms = (time.time() - start) * 1000

        choice = response.choices[0] if response.choices else None
        message_content = choice.message.content if choice and choice.message else ""
        content = self._extract_content(message_content)

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

        result = ChatResult(
            content=content,
            model=resolved_model,
            provider="openai_compatible",
            duration_ms=duration_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
        )
        logger.info(
            "OpenAI-compatible chat request completed",
            extra={
                "provider": "openai_compatible",
                "model": resolved_model,
                "endpoint": self.base_url,
                "duration_ms": duration_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        )
        return result

    async def achat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        start = time.time()
        resolved_model = model or self.model
        normalized_messages = self.normalize_messages(messages)

        call_kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": normalized_messages,
            **kwargs,
        }
        if temperature is not None:
            call_kwargs["temperature"] = temperature

        logger.debug(
            "Dispatching async OpenAI-compatible chat request",
            extra={
                "provider": "openai_compatible",
                "model": resolved_model,
                "endpoint": self.base_url,
                "message_count": len(normalized_messages),
            },
        )
        try:
            response = await self._async_client.chat.completions.create(**call_kwargs)
        except Exception as exc:
            logger.error(
                "Async OpenAI-compatible chat request failed",
                extra={
                    "provider": "openai_compatible",
                    "model": resolved_model,
                    "endpoint": self.base_url,
                    "error": str(exc),
                },
            )
            raise
        duration_ms = (time.time() - start) * 1000

        choice = response.choices[0] if response.choices else None
        message_content = choice.message.content if choice and choice.message else ""
        content = self._extract_content(message_content)

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

        result = ChatResult(
            content=content,
            model=resolved_model,
            provider="openai_compatible",
            duration_ms=duration_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
        )
        logger.info(
            "Async OpenAI-compatible chat request completed",
            extra={
                "provider": "openai_compatible",
                "model": resolved_model,
                "endpoint": self.base_url,
                "duration_ms": duration_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        )
        return result


class HuggingFaceLocalLLMProvider(LLMProvider):
    """LLM provider that runs local inference via transformers."""

    def __init__(
        self,
        *,
        model: str,
        config: Optional[AgenticConfig] = None,
        timeout: Optional[float] = None,
        max_new_tokens: int = 512,
        device_map: Optional[str] = None,
        torch_dtype: Optional[str] = None,
        trust_remote_code: Optional[bool] = None,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout)
        self.max_new_tokens = max_new_tokens
        llm_cfg = getattr(self.config, "llm", None)
        self.device_map = device_map or getattr(llm_cfg, "hf_device_map", "auto")
        self.torch_dtype = torch_dtype or getattr(llm_cfg, "hf_torch_dtype", None)
        self.trust_remote_code = bool(
            trust_remote_code
            if trust_remote_code is not None
            else getattr(llm_cfg, "hf_trust_remote_code", False)
        )

        self._hub = HuggingFaceHubIntegration(
            token=self.config.huggingface.token,
            local_cache_dir=str(self.config.huggingface.cache_dir),
        )
        self._pipeline_cache: dict[str, tuple[Any, Any]] = {}
        self._lock = RLock()

    def _resolve_pipeline(self, model_name: str) -> tuple[Any, Any]:
        with self._lock:
            if model_name in self._pipeline_cache:
                return self._pipeline_cache[model_name]

            try:
                from transformers import pipeline
            except ImportError as exc:
                raise ImportError(
                    "transformers is required for huggingface_local provider. "
                    "Install optional dependencies with: poetry install --extras huggingface"
                ) from exc

            start = time.time()
            model, tokenizer = self._hub.load_model_and_tokenizer(
                model_name,
                device_map=self.device_map,
                torch_dtype=self.torch_dtype,
                trust_remote_code=self.trust_remote_code,
            )
            generator = pipeline(
                task="text-generation",
                model=model,
                tokenizer=tokenizer,
            )
            self._pipeline_cache[model_name] = (generator, tokenizer)
            logger.info(
                "Loaded Hugging Face local model for chat",
                extra={
                    "provider": "huggingface_local",
                    "model": model_name,
                    "load_duration_ms": (time.time() - start) * 1000,
                },
            )
            return generator, tokenizer

    @staticmethod
    def _fallback_prompt(messages: list[dict[str, str]]) -> str:
        lines: list[str] = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        lines.append("ASSISTANT:")
        return "\n".join(lines)

    def _format_prompt(self, tokenizer: Any, messages: list[dict[str, str]]) -> str:
        apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
        if callable(apply_chat_template):
            try:
                return apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except Exception:
                logger.debug("Falling back to manual prompt formatting for HF local chat")
        return self._fallback_prompt(messages)

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ChatResult:
        start = time.time()
        resolved_model = model or self.model
        normalized_messages = self.normalize_messages(messages)

        generator, tokenizer = self._resolve_pipeline(resolved_model)
        prompt = self._format_prompt(tokenizer, normalized_messages)

        max_new_tokens = int(kwargs.pop("max_new_tokens", self.max_new_tokens))
        use_temperature = 0.7 if temperature is None else float(temperature)
        do_sample = use_temperature > 0

        logger.debug(
            "Dispatching Hugging Face local chat request",
            extra={
                "provider": "huggingface_local",
                "model": resolved_model,
                "message_count": len(normalized_messages),
                "max_new_tokens": max_new_tokens,
            },
        )
        try:
            response = generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=use_temperature,
                do_sample=do_sample,
                return_full_text=False,
                **kwargs,
            )
        except Exception as exc:
            logger.error(
                "Hugging Face local chat request failed",
                extra={
                    "provider": "huggingface_local",
                    "model": resolved_model,
                    "error": str(exc),
                },
            )
            raise

        content = ""
        if isinstance(response, list) and response:
            item = response[0]
            if isinstance(item, dict):
                content = str(item.get("generated_text", ""))
            else:
                content = str(item)
        else:
            content = str(response)

        duration_ms = (time.time() - start) * 1000

        prompt_tokens: Optional[int] = None
        completion_tokens: Optional[int] = None
        total_tokens: Optional[int] = None
        try:
            prompt_tokens = len(tokenizer(prompt, add_special_tokens=False).get("input_ids", []))
            completion_tokens = len(tokenizer(content, add_special_tokens=False).get("input_ids", []))
            total_tokens = prompt_tokens + completion_tokens
        except Exception:
            pass

        result = ChatResult(
            content=content,
            model=resolved_model,
            provider="huggingface_local",
            duration_ms=duration_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw_response=response,
        )
        logger.info(
            "Hugging Face local chat request completed",
            extra={
                "provider": "huggingface_local",
                "model": resolved_model,
                "duration_ms": duration_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        )
        return result


LLMProvider.register_provider("ollama", OllamaLLMProvider)
LLMProvider.register_provider("huggingface_local", HuggingFaceLocalLLMProvider)
LLMProvider.register_provider("openai_compatible", OpenAICompatibleLLMProvider)

