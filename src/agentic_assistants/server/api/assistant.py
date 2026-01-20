"""
Framework assistant API router.

Provides a lightweight chat endpoint that uses the configured framework
assistant model (separate from the agent default) and can optionally include
doc excerpts for better answers.

Multi-Deployment Support
------------------------
The assistant supports multiple Ollama deployment endpoints for high availability
and load balancing. Configure multiple endpoints in the assistant config:

    "ollamaEndpoints": [
        {"url": "http://localhost:11434", "priority": 1, "name": "local"},
        {"url": "http://ollama.cluster.local:11434", "priority": 2, "name": "cluster"},
    ]

The assistant will try endpoints in priority order (lower number = higher priority)
and automatically failover to the next endpoint if one is unavailable.

Usage:
    1. Configure endpoints via PUT /api/v1/assistant/config
    2. The chat endpoint will automatically use the best available endpoint
    3. Use GET /api/v1/assistant/endpoints to list and check endpoint health
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])

# Config file path for persistent storage
CONFIG_FILE = Path.home() / ".agentic_assistants" / "assistant_config.json"

# Default Ollama endpoints (priority order - lower is higher priority)
DEFAULT_OLLAMA_ENDPOINTS = [
    {"url": "http://localhost:11434", "priority": 1, "name": "local"},
]

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "defaultFramework": "crewai",
    "model": "llama3.2",
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
    "ollamaEndpoints": DEFAULT_OLLAMA_ENDPOINTS,
}


class AssistantMessage(BaseModel):
    """A chat message to or from the assistant."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class AssistantChatRequest(BaseModel):
    """Request body for assistant chat."""

    messages: List[AssistantMessage] = Field(..., description="Conversation history")
    route: Optional[str] = Field(default=None, description="Current UI route for context")
    project_id: Optional[str] = Field(default=None, description="Active project id if applicable")
    selected_doc_slug: Optional[str] = Field(default=None, description="Doc slug to include for context")


class AssistantChatResponse(BaseModel):
    """Assistant chat response."""

    message: AssistantMessage
    used_doc_slug: Optional[str] = None
    model: str


class OllamaEndpoint(BaseModel):
    """Configuration for an Ollama endpoint."""
    
    url: str = Field(..., description="Ollama API URL (e.g., http://localhost:11434)")
    priority: int = Field(default=1, description="Priority order (1=highest)")
    name: str = Field(default="default", description="Human-readable endpoint name")
    enabled: bool = Field(default=True, description="Whether this endpoint is enabled")


class AssistantConfigRequest(BaseModel):
    """Request body for updating assistant configuration."""

    enabled: Optional[bool] = None
    defaultFramework: Optional[str] = None
    model: Optional[str] = None
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
    ollamaEndpoints: Optional[List[Dict[str, Any]]] = None


def _load_config() -> Dict[str, Any]:
    """Load assistant configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                stored = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **stored}
        except Exception as exc:
            logger.warning(f"Failed to load config: {exc}")
    return DEFAULT_CONFIG.copy()


def _save_config(config: Dict[str, Any]) -> None:
    """Save assistant configuration to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get the current assistant configuration."""
    return _load_config()


@router.put("/config")
async def update_config(request: AssistantConfigRequest) -> Dict[str, Any]:
    """Update the assistant configuration."""
    try:
        current = _load_config()
        
        # Update only provided fields
        updates = request.model_dump(exclude_none=True)
        current.update(updates)
        
        _save_config(current)
        logger.info("Assistant configuration updated")
        
        return current
    except Exception as exc:
        logger.error(f"Failed to save config: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {exc}")


def _get_sorted_endpoints(assistant_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get endpoints sorted by priority (lower priority number = try first)."""
    endpoints = assistant_config.get("ollamaEndpoints", DEFAULT_OLLAMA_ENDPOINTS)
    # Filter enabled endpoints and sort by priority
    enabled = [ep for ep in endpoints if ep.get("enabled", True)]
    return sorted(enabled, key=lambda x: x.get("priority", 999))


async def _check_endpoint_health(endpoint_url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Check if an Ollama endpoint is healthy."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{endpoint_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "status": "healthy",
                    "url": endpoint_url,
                    "models": models,
                    "model_count": len(models),
                }
            return {"status": "unhealthy", "url": endpoint_url, "error": f"HTTP {response.status_code}"}
    except httpx.TimeoutException:
        return {"status": "unhealthy", "url": endpoint_url, "error": "Connection timeout"}
    except Exception as exc:
        return {"status": "unhealthy", "url": endpoint_url, "error": str(exc)}


async def _find_healthy_endpoint(assistant_config: Dict[str, Any]) -> Optional[str]:
    """Find the first healthy endpoint in priority order."""
    endpoints = _get_sorted_endpoints(assistant_config)
    
    for endpoint in endpoints:
        url = endpoint.get("url", "")
        if not url:
            continue
        
        health = await _check_endpoint_health(url, timeout=3.0)
        if health.get("status") == "healthy":
            logger.debug(f"Using Ollama endpoint: {endpoint.get('name', url)}")
            return url
    
    return None


@router.get("/endpoints")
async def list_endpoints() -> Dict[str, Any]:
    """
    List all configured Ollama endpoints and their health status.
    
    Returns endpoint configurations with real-time health checks.
    Useful for debugging connection issues and monitoring deployment status.
    """
    assistant_config = _load_config()
    endpoints = _get_sorted_endpoints(assistant_config)
    
    results = []
    for endpoint in endpoints:
        url = endpoint.get("url", "")
        health = await _check_endpoint_health(url) if url else {"status": "invalid", "error": "No URL"}
        results.append({
            **endpoint,
            "health": health,
        })
    
    return {
        "endpoints": results,
        "total": len(results),
        "healthy_count": sum(1 for r in results if r.get("health", {}).get("status") == "healthy"),
    }


@router.post("/endpoints/add")
async def add_endpoint(endpoint: OllamaEndpoint) -> Dict[str, Any]:
    """
    Add a new Ollama endpoint to the configuration.
    
    Use this to configure additional Ollama deployments for failover support.
    """
    config = _load_config()
    endpoints = config.get("ollamaEndpoints", [])
    
    # Check for duplicate URLs
    if any(ep.get("url") == endpoint.url for ep in endpoints):
        raise HTTPException(status_code=400, detail=f"Endpoint with URL {endpoint.url} already exists")
    
    endpoints.append(endpoint.model_dump())
    config["ollamaEndpoints"] = endpoints
    _save_config(config)
    
    return {"status": "ok", "message": f"Added endpoint: {endpoint.name}", "endpoints": endpoints}


@router.delete("/endpoints/{endpoint_name}")
async def remove_endpoint(endpoint_name: str) -> Dict[str, Any]:
    """Remove an Ollama endpoint by name."""
    config = _load_config()
    endpoints = config.get("ollamaEndpoints", [])
    
    original_count = len(endpoints)
    endpoints = [ep for ep in endpoints if ep.get("name") != endpoint_name]
    
    if len(endpoints) == original_count:
        raise HTTPException(status_code=404, detail=f"Endpoint '{endpoint_name}' not found")
    
    if len(endpoints) == 0:
        # Always keep at least the default endpoint
        endpoints = DEFAULT_OLLAMA_ENDPOINTS.copy()
    
    config["ollamaEndpoints"] = endpoints
    _save_config(config)
    
    return {"status": "ok", "message": f"Removed endpoint: {endpoint_name}", "endpoints": endpoints}


@router.get("/test")
async def test_connection() -> Dict[str, Any]:
    """
    Test the assistant connection to Ollama.
    
    Tries all configured endpoints and returns the status of each.
    """
    assistant_config = _load_config()
    model = assistant_config.get("model", "llama3.2")
    
    # Find a healthy endpoint
    healthy_endpoint = await _find_healthy_endpoint(assistant_config)
    
    if healthy_endpoint:
        return {
            "status": "ok",
            "model": model,
            "ollama_host": healthy_endpoint,
            "message": "Connected to Ollama successfully",
        }
    
    # No healthy endpoints - return detailed error
    endpoints = _get_sorted_endpoints(assistant_config)
    endpoint_errors = []
    for ep in endpoints:
        health = await _check_endpoint_health(ep.get("url", ""))
        endpoint_errors.append({
            "name": ep.get("name", "unknown"),
            "url": ep.get("url", ""),
            "error": health.get("error", "Unknown error"),
        })
    
    raise HTTPException(
        status_code=503,
        detail={
            "message": "No healthy Ollama endpoints available",
            "endpoints_tried": endpoint_errors,
            "suggestion": "Ensure Ollama is running and accessible at one of the configured endpoints",
        }
    )


def _resolve_docs_dir() -> Optional[Path]:
    """Locate the docs directory relative to the project root."""
    candidates = [
        Path(__file__).resolve().parents[5] / "docs",
        Path.cwd() / "docs",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _load_doc(slug: str) -> Optional[str]:
    """Load markdown content for a doc slug, if available."""
    docs_dir = _resolve_docs_dir()
    if not docs_dir:
        return None

    doc_path = docs_dir / f"{slug}.md"
    if not doc_path.exists():
        return None

    try:
        return doc_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning(f"Failed to read doc {doc_path}: {exc}")
        return None


@router.post("/chat", response_model=AssistantChatResponse)
async def assistant_chat(request: AssistantChatRequest) -> AssistantChatResponse:
    """
    Chat with the framework assistant model.

    Features:
    - Uses the model from assistant config (falls back to llama3.2)
    - Automatic failover across configured Ollama endpoints
    - Optionally injects documentation context when `selected_doc_slug` is provided
    - Custom system prompts supported via configuration
    
    Error Handling:
    - Returns 503 if no Ollama endpoints are available
    - Returns 504 on timeout (configurable, default 120s)
    - Returns 502 on model errors with detailed messages
    """
    # Load assistant-specific configuration
    assistant_config = _load_config()
    
    # Use model from assistant config, not global config
    model = assistant_config.get("model", "llama3.2")
    custom_system_prompt = assistant_config.get("systemPrompt", "")
    
    # Find a healthy Ollama endpoint
    ollama_host = await _find_healthy_endpoint(assistant_config)
    
    if not ollama_host:
        logger.error("No healthy Ollama endpoints available for chat")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "No Ollama connection available",
                "message": "Could not connect to any configured Ollama endpoint. Please ensure Ollama is running.",
                "suggestion": "Run 'ollama serve' or check your Ollama deployment",
            }
        )
    
    doc_excerpt = None
    if request.selected_doc_slug:
        doc_content = _load_doc(request.selected_doc_slug)
        if doc_content:
            doc_excerpt = doc_content[:2000]  # keep payload lean

    # Build system prompt
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

    system_prompt = "\n".join(system_parts)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([msg.model_dump() for msg in request.messages])

    if doc_excerpt:
        messages.append(
            {
                "role": "system",
                "content": f"Relevant documentation ({request.selected_doc_slug}):\n{doc_excerpt}",
            }
        )

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    # Get timeout from global config
    global_config = AgenticConfig()
    timeout = global_config.ollama.timeout

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.debug(f"Sending chat request to {ollama_host} with model {model}")
            response = await client.post(f"{ollama_host}/api/chat", json=payload)
            
            if response.status_code == 404:
                # Model not found - provide helpful error
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Model not found",
                        "message": f"The model '{model}' is not available on the Ollama server.",
                        "suggestion": f"Run 'ollama pull {model}' to download the model, or select a different model in assistant settings.",
                    }
                )
            
            response.raise_for_status()
            data = response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Chat request timed out after {timeout}s")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Request timeout",
                "message": f"The assistant request timed out after {timeout} seconds.",
                "suggestion": "Try a shorter message or check if the model is still loading.",
            }
        )
    except httpx.ConnectError as exc:
        logger.error(f"Connection error to Ollama: {exc}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Connection failed",
                "message": "Lost connection to Ollama during the request.",
                "suggestion": "Check if Ollama is still running and try again.",
            }
        )
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error from Ollama: {exc}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Ollama error",
                "message": f"Ollama returned an error: {exc.response.status_code}",
                "suggestion": "Check Ollama logs for more details.",
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in assistant chat: {exc}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Unexpected error",
                "message": str(exc),
            }
        )

    content = (
        data.get("message", {}).get("content")
        or data.get("response")
        or ""
    )

    if not content:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Empty response",
                "message": "The assistant returned an empty response.",
                "suggestion": "Try rephrasing your question or check if the model is working correctly.",
            }
        )

    return AssistantChatResponse(
        message=AssistantMessage(role="assistant", content=content),
        used_doc_slug=request.selected_doc_slug,
        model=model,
    )

