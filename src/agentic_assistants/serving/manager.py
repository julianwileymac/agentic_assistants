"""
Model serving manager.

This module provides a unified interface for managing model deployments
across different serving backends.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.serving.config import ServingConfig, ServingBackend, EndpointConfig
from agentic_assistants.serving.backends.ollama import OllamaBackend, DeploymentResult
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ServingManager:
    """
    Unified manager for model serving.
    
    Manages deployments across:
    - Ollama
    - vLLM
    - TGI
    
    Provides:
    - Backend abstraction
    - Endpoint management
    - Health monitoring
    - Load balancing (future)
    """
    
    def __init__(self, config: Optional[ServingConfig] = None):
        """
        Initialize the serving manager.
        
        Args:
            config: Serving configuration
        """
        self.config = config or ServingConfig()
        self._backends: Dict[str, Any] = {}
        self._endpoints: Dict[str, EndpointConfig] = {}
        
        # Initialize backends
        self._init_backends()
    
    def _init_backends(self) -> None:
        """Initialize serving backends."""
        # Ollama
        self._backends["ollama"] = OllamaBackend(self.config.ollama)
        
        # vLLM and TGI are initialized on demand
        logger.info("Serving manager initialized")
    
    def get_backend(self, name: str) -> Optional[Any]:
        """Get a serving backend by name."""
        return self._backends.get(name)
    
    async def check_backend_health(self, backend: str) -> bool:
        """Check if a backend is healthy."""
        if backend == "ollama":
            ollama = self._backends.get("ollama")
            if ollama:
                return await ollama.is_available()
        return False
    
    async def list_available_backends(self) -> List[Dict[str, Any]]:
        """List all available backends with their status."""
        backends = []
        
        for name, backend in self._backends.items():
            status = await self.check_backend_health(name)
            backends.append({
                "name": name,
                "available": status,
                "config": getattr(self.config, name, None),
            })
        
        return backends
    
    async def deploy_model(
        self,
        model_path: str,
        model_name: str,
        backend: Optional[str] = None,
        **kwargs,
    ) -> DeploymentResult:
        """
        Deploy a model to a serving backend.
        
        Args:
            model_path: Path to the model
            model_name: Name for the deployed model
            backend: Target backend (default: from config)
            **kwargs: Backend-specific arguments
        
        Returns:
            DeploymentResult
        """
        backend = backend or self.config.default_backend.value
        
        if backend == "ollama":
            ollama = self._backends.get("ollama")
            if not ollama:
                return DeploymentResult(
                    success=False,
                    model_name=model_name,
                    error="Ollama backend not initialized",
                )
            
            return await ollama.deploy_custom_model(
                model_path=model_path,
                model_name=model_name,
                **kwargs,
            )
        
        elif backend == "vllm":
            return await self._deploy_vllm(model_path, model_name, **kwargs)
        
        elif backend == "tgi":
            return await self._deploy_tgi(model_path, model_name, **kwargs)
        
        else:
            return DeploymentResult(
                success=False,
                model_name=model_name,
                error=f"Unknown backend: {backend}",
            )
    
    async def _deploy_vllm(
        self,
        model_path: str,
        model_name: str,
        **kwargs,
    ) -> DeploymentResult:
        """Deploy to vLLM."""
        # vLLM deployment typically involves starting a server
        vllm_config = self.config.vllm
        
        command = [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_path,
            "--port", str(vllm_config.port),
            "--gpu-memory-utilization", str(vllm_config.gpu_memory_utilization),
        ]
        
        if vllm_config.tensor_parallel_size > 1:
            command.extend(["--tensor-parallel-size", str(vllm_config.tensor_parallel_size)])
        
        if vllm_config.max_model_len:
            command.extend(["--max-model-len", str(vllm_config.max_model_len)])
        
        return DeploymentResult(
            success=True,
            model_name=model_name,
            endpoint=vllm_config.base_url,
            details={
                "command": " ".join(command),
                "instructions": [
                    f"Run the following command to start vLLM:",
                    " ".join(command),
                    f"API will be available at {vllm_config.base_url}",
                ],
            },
        )
    
    async def _deploy_tgi(
        self,
        model_path: str,
        model_name: str,
        **kwargs,
    ) -> DeploymentResult:
        """Deploy to TGI."""
        tgi_config = self.config.tgi
        
        # TGI typically runs via Docker
        docker_command = [
            "docker", "run", "--gpus", "all",
            "-p", f"{tgi_config.port}:80",
            "-v", f"{model_path}:/model",
            "ghcr.io/huggingface/text-generation-inference:latest",
            "--model-id", "/model",
            "--max-input-length", str(tgi_config.max_input_length),
            "--max-total-tokens", str(tgi_config.max_total_tokens),
        ]
        
        if tgi_config.quantize:
            docker_command.extend(["--quantize", tgi_config.quantize])
        
        return DeploymentResult(
            success=True,
            model_name=model_name,
            endpoint=tgi_config.base_url,
            details={
                "command": " ".join(docker_command),
                "instructions": [
                    "Run the following Docker command to start TGI:",
                    " ".join(docker_command),
                    f"API will be available at {tgi_config.base_url}",
                ],
            },
        )
    
    async def list_deployed_models(self, backend: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all deployed models."""
        models = []
        
        if backend is None or backend == "ollama":
            ollama = self._backends.get("ollama")
            if ollama:
                ollama_models = await ollama.list_models()
                for m in ollama_models:
                    models.append({
                        "name": m.name,
                        "backend": "ollama",
                        "size": m.size,
                        "digest": m.digest,
                    })
        
        return models
    
    async def undeploy_model(self, model_name: str, backend: str) -> bool:
        """Remove a deployed model."""
        if backend == "ollama":
            ollama = self._backends.get("ollama")
            if ollama:
                return await ollama.delete_model(model_name)
        
        return False
    
    def create_endpoint(
        self,
        name: str,
        model_id: str,
        backend: ServingBackend,
        **kwargs,
    ) -> EndpointConfig:
        """Create an endpoint configuration."""
        endpoint = EndpointConfig(
            name=name,
            model_id=model_id,
            backend=backend,
            **kwargs,
        )
        self._endpoints[name] = endpoint
        return endpoint
    
    def get_endpoint(self, name: str) -> Optional[EndpointConfig]:
        """Get an endpoint by name."""
        return self._endpoints.get(name)
    
    def list_endpoints(self) -> List[EndpointConfig]:
        """List all endpoints."""
        return list(self._endpoints.values())
    
    async def close(self):
        """Close all backend connections."""
        for backend in self._backends.values():
            if hasattr(backend, 'close'):
                await backend.close()
