"""
Framework assistant API router with provider-agnostic model execution.

Features:
- Configurable provider/model selection (Ollama, HF local, OpenAI-compatible)
- Endpoint failover for remote providers
- Optional documentation and code context injection
- Backward-compatible support for legacy assistant config keys
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.llms import LLMProvider
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])

CONFIG_FILE = Path.home() / ".agentic_assistants" / "assistant_config.json"

DEFAULT_LLM_ENDPOINTS = [
    {
        "url": "http://localhost:11434",
        "priority": 1,
        "name": "local-ollama",
        "provider": "ollama",
        "enabled": True,
    },
]
DEFAULT_OLLAMA_ENDPOINTS = [
    {k: v for k, v in ep.items() if k != "provider"}
    for ep in DEFAULT_LLM_ENDPOINTS
]

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "defaultFramework": "crewai",
    "provider": "ollama",
    "model": "llama3.2",
    "endpoint": None,
    "openaiCompatibleBaseUrl": "http://localhost:8000/v1",
    "openaiCompatibleApiKeyEnv": "OPENAI_API_KEY",
    "hfExecutionMode": "hybrid",
    "hfLocalModel": None,
    "enableCodingHelper": True,
    "enableFrameworkGuide": True,
    "enableMetaAnalysis": True,
    "ragEnabled": True,
    "memoryEnabled": True,
    "codeKbProjectId": "",
    "docsKbName": "framework_docs",
    "usageTrackingEnabled": True,
    "metaAnalysisIntervalHours": 24,
    "maxContextMessages": 20,
    "systemPrompt": "",
    "llmEndpoints": DEFAULT_LLM_ENDPOINTS,
    # legacy key retained for compatibility with existing clients
    "ollamaEndpoints": DEFAULT_OLLAMA_ENDPOINTS,
}


class AssistantMessage(BaseModel):
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class AssistantChatRequest(BaseModel):
    messages: List[AssistantMessage] = Field(..., description="Conversation history")
    route: Optional[str] = Field(default=None, description="Current UI route for context")
    project_id: Optional[str] = Field(default=None, description="Active project id if applicable")
    selected_doc_slug: Optional[str] = Field(default=None, description="Doc slug to include for context")
    include_code_context: Optional[bool] = Field(default=False, description="Include codebase context pack")
    include_project_docs: Optional[bool] = Field(default=False, description="Include project docs context")
    context_task: Optional[str] = Field(default=None, description="Context pack task (e.g. understand)")

    # Optional per-request inference overrides
    provider: Optional[str] = Field(default=None, description="Provider override (ollama, huggingface_local, openai_compatible)")
    model: Optional[str] = Field(default=None, description="Model override")
    endpoint: Optional[str] = Field(default=None, description="Endpoint override for remote providers")
    api_key_env: Optional[str] = Field(default=None, description="API key environment variable for OpenAI-compatible provider")


class AssistantChatResponse(BaseModel):
    message: AssistantMessage
    used_doc_slug: Optional[str] = None
    model: str
    provider: str


class LLMEndpoint(BaseModel):
    url: str = Field(..., description="Endpoint URL")
    priority: int = Field(default=1, description="Priority order (1=highest)")
    name: str = Field(default="default", description="Human-readable endpoint name")
    provider: str = Field(default="ollama", description="Endpoint provider")
    enabled: bool = Field(default=True, description="Whether this endpoint is enabled")


class AssistantConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    defaultFramework: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    endpoint: Optional[str] = None
    openaiCompatibleBaseUrl: Optional[str] = None
    openaiCompatibleApiKeyEnv: Optional[str] = None
    hfExecutionMode: Optional[str] = None
    hfLocalModel: Optional[str] = None
    enableCodingHelper: Optional[bool] = None
    enableFrameworkGuide: Optional[bool] = None
    enableMetaAnalysis: Optional[bool] = None
    ragEnabled: Optional[bool] = None
    memoryEnabled: Optional[bool] = None
    codeKbProjectId: Optional[str] = None
    docsKbName: Optional[str] = None
    usageTrackingEnabled: Optional[bool] = None
    metaAnalysisIntervalHours: Optional[int] = None
    maxContextMessages: Optional[int] = None
    systemPrompt: Optional[str] = None
    llmEndpoints: Optional[List[Dict[str, Any]]] = None
    # legacy key
    ollamaEndpoints: Optional[List[Dict[str, Any]]] = None


def _normalized_provider(provider: Optional[str]) -> str:
    if not provider:
        return "ollama"
    normalized = provider.strip().lower().replace("-", "_")
    if normalized in {"openai", "openai_compat"}:
        return "openai_compatible"
    if normalized in {"huggingface", "hf_local"}:
        return "huggingface_local"
    return normalized


def _normalize_endpoint_record(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(endpoint)
    normalized["provider"] = _normalized_provider(normalized.get("provider", "ollama"))
    normalized["enabled"] = bool(normalized.get("enabled", True))
    normalized["priority"] = int(normalized.get("priority", 999))
    normalized["name"] = str(normalized.get("name", "default"))
    normalized["url"] = str(normalized.get("url", "")).rstrip("/")
    return normalized


def _normalize_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    config = {**DEFAULT_CONFIG, **raw_config}
    config["provider"] = _normalized_provider(config.get("provider"))

    llm_endpoints: List[Dict[str, Any]] = []
    if isinstance(config.get("llmEndpoints"), list) and config.get("llmEndpoints"):
        llm_endpoints = [
            _normalize_endpoint_record(ep)
            for ep in config["llmEndpoints"]
            if isinstance(ep, dict)
        ]
    elif isinstance(config.get("ollamaEndpoints"), list) and config.get("ollamaEndpoints"):
        llm_endpoints = [
            _normalize_endpoint_record({**ep, "provider": "ollama"})
            for ep in config["ollamaEndpoints"]
            if isinstance(ep, dict)
        ]
    else:
        llm_endpoints = [_normalize_endpoint_record(ep) for ep in DEFAULT_LLM_ENDPOINTS]

    if not llm_endpoints:
        llm_endpoints = [_normalize_endpoint_record(ep) for ep in DEFAULT_LLM_ENDPOINTS]

    config["llmEndpoints"] = llm_endpoints
    config["ollamaEndpoints"] = [
        {k: v for k, v in ep.items() if k != "provider"}
        for ep in llm_endpoints
        if ep.get("provider") == "ollama"
    ]
    return config


def _load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                stored = json.load(file)
                return _normalize_config(stored)
        except Exception as exc:
            logger.warning("Failed to load assistant config: %s", exc)
    return _normalize_config({})


def _save_config(config: Dict[str, Any]) -> None:
    normalized = _normalize_config(config)
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2)


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    return _load_config()


@router.put("/config")
async def update_config(request: AssistantConfigRequest) -> Dict[str, Any]:
    try:
        current = _load_config()
        updates = request.model_dump(exclude_none=True)
        current.update(updates)
        normalized = _normalize_config(current)
        _save_config(normalized)
        logger.info(
            "Assistant configuration updated",
            extra={
                "provider": normalized.get("provider"),
                "model": normalized.get("model"),
            },
        )
        return normalized
    except Exception as exc:
        logger.error("Failed to save assistant config: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {exc}")


def _get_sorted_endpoints(assistant_config: Dict[str, Any], provider: Optional[str] = None) -> List[Dict[str, Any]]:
    endpoints = assistant_config.get("llmEndpoints", [])
    active = [ep for ep in endpoints if ep.get("enabled", True)]
    if provider:
        wanted = _normalized_provider(provider)
        active = [ep for ep in active if _normalized_provider(ep.get("provider")) == wanted]
    return sorted(active, key=lambda endpoint: int(endpoint.get("priority", 999)))


async def _check_endpoint_health(endpoint: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
    provider = _normalized_provider(endpoint.get("provider"))
    endpoint_url = str(endpoint.get("url", "")).rstrip("/")

    if provider == "huggingface_local":
        return {
            "status": "healthy",
            "provider": provider,
            "url": endpoint_url or "local",
            "note": "Local Hugging Face execution does not require HTTP endpoint health checks",
        }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if provider == "ollama":
                response = await client.get(f"{endpoint_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]
                    return {
                        "status": "healthy",
                        "provider": provider,
                        "url": endpoint_url,
                        "models": models,
                        "model_count": len(models),
                    }
                return {
                    "status": "unhealthy",
                    "provider": provider,
                    "url": endpoint_url,
                    "error": f"HTTP {response.status_code}",
                }

            # OpenAI-compatible endpoints vary between /models and /v1/models.
            response = await client.get(f"{endpoint_url}/models")
            if response.status_code >= 400:
                response = await client.get(f"{endpoint_url}/v1/models")
            if response.status_code == 200:
                data = response.json()
                model_items = data.get("data", []) if isinstance(data, dict) else []
                models = [item.get("id", "") for item in model_items if isinstance(item, dict)]
                return {
                    "status": "healthy",
                    "provider": provider,
                    "url": endpoint_url,
                    "models": models,
                    "model_count": len(models),
                }
            return {
                "status": "unhealthy",
                "provider": provider,
                "url": endpoint_url,
                "error": f"HTTP {response.status_code}",
            }
    except httpx.TimeoutException:
        return {"status": "unhealthy", "provider": provider, "url": endpoint_url, "error": "Connection timeout"}
    except Exception as exc:
        return {"status": "unhealthy", "provider": provider, "url": endpoint_url, "error": str(exc)}


async def _find_healthy_endpoint(assistant_config: Dict[str, Any], provider: str) -> Optional[str]:
    endpoints = _get_sorted_endpoints(assistant_config, provider=provider)
    for endpoint in endpoints:
        health = await _check_endpoint_health(endpoint, timeout=3.0)
        if health.get("status") == "healthy":
            return str(endpoint.get("url", "")).rstrip("/")
    return None


def _effective_provider(assistant_config: Dict[str, Any], request: Optional[AssistantChatRequest] = None) -> str:
    if request and request.provider:
        return _normalized_provider(request.provider)
    return _normalized_provider(assistant_config.get("provider"))


def _effective_model(
    global_config: AgenticConfig,
    assistant_config: Dict[str, Any],
    request: Optional[AssistantChatRequest] = None,
) -> str:
    if request and request.model:
        return request.model
    if assistant_config.get("model"):
        return str(assistant_config["model"])
    if global_config.assistant.model:
        return str(global_config.assistant.model)
    if global_config.llm.model:
        return str(global_config.llm.model)
    return str(global_config.ollama.default_model)


@router.get("/endpoints")
async def list_endpoints() -> Dict[str, Any]:
    assistant_config = _load_config()
    endpoints = _get_sorted_endpoints(assistant_config)
    results = []
    for endpoint in endpoints:
        health = await _check_endpoint_health(endpoint) if endpoint.get("url") else {"status": "invalid", "error": "No URL"}
        results.append({**endpoint, "health": health})
    return {
        "endpoints": results,
        "total": len(results),
        "healthy_count": sum(1 for item in results if item.get("health", {}).get("status") == "healthy"),
    }


@router.post("/endpoints/add")
async def add_endpoint(endpoint: LLMEndpoint) -> Dict[str, Any]:
    assistant_config = _load_config()
    endpoints = assistant_config.get("llmEndpoints", [])
    endpoint_dict = _normalize_endpoint_record(endpoint.model_dump())

    if any(
        _normalized_provider(ep.get("provider")) == endpoint_dict["provider"]
        and ep.get("url") == endpoint_dict["url"]
        for ep in endpoints
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Endpoint {endpoint_dict['url']} already exists for provider {endpoint_dict['provider']}",
        )

    endpoints.append(endpoint_dict)
    assistant_config["llmEndpoints"] = endpoints
    _save_config(assistant_config)
    return {
        "status": "ok",
        "message": f"Added endpoint: {endpoint_dict.get('name', endpoint_dict['url'])}",
        "endpoints": _load_config().get("llmEndpoints", []),
    }


@router.delete("/endpoints/{endpoint_name}")
async def remove_endpoint(endpoint_name: str) -> Dict[str, Any]:
    assistant_config = _load_config()
    endpoints = assistant_config.get("llmEndpoints", [])
    filtered = [ep for ep in endpoints if ep.get("name") != endpoint_name]

    if len(filtered) == len(endpoints):
        raise HTTPException(status_code=404, detail=f"Endpoint '{endpoint_name}' not found")

    if not filtered:
        filtered = [_normalize_endpoint_record(ep) for ep in DEFAULT_LLM_ENDPOINTS]

    assistant_config["llmEndpoints"] = filtered
    _save_config(assistant_config)
    return {
        "status": "ok",
        "message": f"Removed endpoint: {endpoint_name}",
        "endpoints": _load_config().get("llmEndpoints", []),
    }


@router.get("/models/catalog")
async def list_model_catalog() -> Dict[str, Any]:
    config = AgenticConfig()
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    # Ollama models
    try:
        manager = OllamaManager(config)
        models = manager.list_models()
        for model in models:
            model_name = model.name
            key = ("ollama", model_name)
            if key in seen:
                continue
            seen.add(key)
            entries.append(
                {
                    "provider": "ollama",
                    "model": model_name,
                    "source": "ollama",
                    "size": model.size,
                    "modified_at": model.modified_at.isoformat() if model.modified_at else None,
                }
            )
    except Exception as exc:
        logger.debug("Could not enumerate Ollama models for assistant catalog: %s", exc)

    # Custom model registry entries
    registry_path = Path("./data/models/registry.json")
    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
            for model in data.get("models", []):
                if not isinstance(model, dict):
                    continue
                model_name = model.get("name") or model.get("id")
                if not model_name:
                    continue
                key = ("custom", str(model_name))
                if key in seen:
                    continue
                seen.add(key)
                entries.append(
                    {
                        "provider": "custom",
                        "model": model_name,
                        "source": "custom_registry",
                        "status": model.get("status"),
                        "base_model": model.get("base_model"),
                        "hf_repo_id": model.get("hf_repo_id"),
                        "local_path": model.get("local_path"),
                    }
                )
        except Exception as exc:
            logger.debug("Failed to read custom model registry: %s", exc)

    # Hugging Face local cache candidates
    try:
        for candidate in config.huggingface.cache_dir.glob("models--*"):
            model_name = candidate.name.replace("models--", "").replace("--", "/")
            key = ("huggingface_local", model_name)
            if key in seen:
                continue
            seen.add(key)
            entries.append(
                {
                    "provider": "huggingface_local",
                    "model": model_name,
                    "source": "hf_cache",
                    "path": str(candidate),
                }
            )
    except Exception as exc:
        logger.debug("Failed to enumerate Hugging Face cache models: %s", exc)

    # Include configured defaults so the picker has at least one option per provider.
    defaults = [
        ("ollama", config.ollama.default_model),
        ("huggingface_local", config.llm.hf_local_model or ""),
        ("openai_compatible", config.llm.model or ""),
    ]
    for provider, model in defaults:
        if not model:
            continue
        key = (provider, model)
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "provider": provider,
                "model": model,
                "source": "default_config",
            }
        )

    return {"models": entries, "total": len(entries)}


@router.get("/test")
async def test_connection() -> Dict[str, Any]:
    assistant_config = _load_config()
    global_config = AgenticConfig()
    provider = _effective_provider(assistant_config)
    model = _effective_model(global_config, assistant_config)

    endpoint = assistant_config.get("endpoint")
    if provider in {"ollama", "openai_compatible"} and not endpoint:
        endpoint = await _find_healthy_endpoint(assistant_config, provider)

    if provider == "ollama" and not endpoint:
        endpoints = _get_sorted_endpoints(assistant_config, provider="ollama")
        endpoint_errors = []
        for ep in endpoints:
            health = await _check_endpoint_health(ep)
            endpoint_errors.append(
                {
                    "name": ep.get("name", "unknown"),
                    "url": ep.get("url", ""),
                    "error": health.get("error", "Unknown error"),
                }
            )
        raise HTTPException(
            status_code=503,
            detail={
                "message": "No healthy Ollama endpoints available",
                "endpoints_tried": endpoint_errors,
                "suggestion": "Ensure Ollama is running and accessible at one of the configured endpoints",
            },
        )

    if provider == "openai_compatible" and not endpoint:
        endpoint = assistant_config.get("openaiCompatibleBaseUrl") or global_config.llm.openai_base_url

    return {
        "status": "ok",
        "provider": provider,
        "model": model,
        "endpoint": endpoint,
        "message": f"Assistant is configured for provider '{provider}'",
    }


def _resolve_docs_dir() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parents[5] / "docs",
        Path.cwd() / "docs",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _load_doc(slug: str) -> Optional[str]:
    docs_dir = _resolve_docs_dir()
    if not docs_dir:
        return None
    doc_path = docs_dir / f"{slug}.md"
    if not doc_path.exists():
        return None
    try:
        return doc_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to read doc %s: %s", doc_path, exc)
        return None


def _load_project_docs_excerpt(max_chars: int = 2000) -> Optional[str]:
    docs_dir = _resolve_docs_dir()
    if not docs_dir:
        return None

    candidates = []
    index_path = docs_dir / "index.md"
    if index_path.exists():
        candidates.append(index_path)

    for path in sorted(docs_dir.glob("*.md")):
        if path.name == "index.md":
            continue
        candidates.append(path)
        if len(candidates) >= 3:
            break

    parts: list[str] = []
    for path in candidates:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed to read doc %s: %s", path, exc)
            continue
        parts.append(f"## {path.stem}\n{content[:max_chars]}")
        if sum(len(part) for part in parts) >= max_chars:
            break

    combined = "\n\n".join(parts)
    return combined[:max_chars] if combined else None


def _load_code_context(task: Optional[str] = None, max_chars: int = 4000) -> Optional[str]:
    try:
        from agentic_assistants.utils.context_loader import ContextLoader
    except Exception as exc:
        logger.warning("Failed to import ContextLoader: %s", exc)
        return None

    try:
        loader = ContextLoader()
        context = loader.load_for_task(task) if task else loader.load_core_context()
        return context[:max_chars] if context else None
    except Exception as exc:
        logger.warning("Failed to load context pack: %s", exc)
        return None


@router.post("/chat", response_model=AssistantChatResponse)
async def assistant_chat(request: AssistantChatRequest) -> AssistantChatResponse:
    assistant_config = _load_config()
    global_config = AgenticConfig()

    provider = _effective_provider(assistant_config, request=request)
    model = _effective_model(global_config, assistant_config, request=request)
    custom_system_prompt = assistant_config.get("systemPrompt", "")

    endpoint = request.endpoint or assistant_config.get("endpoint")
    if provider in {"ollama", "openai_compatible"} and not endpoint:
        endpoint = await _find_healthy_endpoint(assistant_config, provider)
    if provider == "openai_compatible" and not endpoint:
        endpoint = assistant_config.get("openaiCompatibleBaseUrl") or global_config.llm.openai_base_url

    if provider == "ollama" and not endpoint:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "No Ollama connection available",
                "message": "Could not connect to any configured Ollama endpoint. Please ensure Ollama is running.",
                "suggestion": "Run 'ollama serve' or check your Ollama deployment",
            },
        )

    logger.info(
        "Assistant chat request received",
        extra={
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
            "route": request.route,
            "project_id": request.project_id,
        },
    )

    doc_excerpt = None
    if request.selected_doc_slug:
        doc_content = _load_doc(request.selected_doc_slug)
        if doc_content:
            doc_excerpt = doc_content[:2000]

    code_context = _load_code_context(request.context_task) if request.include_code_context else None
    docs_excerpt = _load_project_docs_excerpt() if request.include_project_docs else None

    if custom_system_prompt:
        system_parts = [custom_system_prompt]
    else:
        system_parts = [
            "You are the Agentic Assistants framework helper.",
            "Help users understand how to use the Control Panel, projects, agents, flows, training, and serving.",
            "Be concise and actionable.",
        ]
    system_parts.append(f"Active route: {request.route or 'unknown'}")
    if request.project_id:
        system_parts.append(f"Active project id: {request.project_id}")
    if doc_excerpt:
        system_parts.append("Use the provided documentation excerpt when answering.")
    if code_context:
        system_parts.append("Use the provided code context pack when answering.")
    if docs_excerpt:
        system_parts.append("Use the provided project docs context when answering.")

    messages: list[dict[str, Any]] = [{"role": "system", "content": "\n".join(system_parts)}]
    messages.extend([msg.model_dump() for msg in request.messages])

    if doc_excerpt:
        messages.append({"role": "system", "content": f"Relevant documentation ({request.selected_doc_slug}):\n{doc_excerpt}"})
    if code_context:
        messages.append({"role": "system", "content": f"Codebase context:\n{code_context}"})
    if docs_excerpt:
        messages.append({"role": "system", "content": f"Project docs context:\n{docs_excerpt}"})

    api_key_env = request.api_key_env or assistant_config.get("openaiCompatibleApiKeyEnv") or global_config.llm.openai_api_key_env

    try:
        provider_client = LLMProvider.from_config(
            global_config,
            provider=provider,
            model=model,
            endpoint=endpoint,
            api_key_env=api_key_env,
        )
        llm_result = await provider_client.achat(messages=messages, model=model)
    except ImportError as exc:
        logger.error("Provider dependency missing: %s", exc)
        raise HTTPException(status_code=500, detail={"error": "Missing dependency", "message": str(exc)})
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Assistant chat failed",
            extra={
                "provider": provider,
                "model": model,
                "endpoint": endpoint,
                "error": str(exc),
            },
        )
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Inference error",
                "message": str(exc),
                "provider": provider,
                "model": model,
            },
        )

    if not llm_result.content:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Empty response",
                "message": "The assistant returned an empty response.",
                "suggestion": "Try rephrasing your question or validate the selected model/provider.",
            },
        )

    logger.info(
        "Assistant chat completed",
        extra={
            "provider": llm_result.provider,
            "model": llm_result.model,
            "duration_ms": llm_result.duration_ms,
            "prompt_tokens": llm_result.prompt_tokens,
            "completion_tokens": llm_result.completion_tokens,
        },
    )

    return AssistantChatResponse(
        message=AssistantMessage(role="assistant", content=llm_result.content),
        used_doc_slug=request.selected_doc_slug,
        model=llm_result.model,
        provider=llm_result.provider,
    )

