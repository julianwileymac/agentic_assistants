"""
Enhanced Ollama serving backend.

This module provides enhanced Ollama integration for deploying custom models.
"""

import asyncio
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from agentic_assistants.serving.config import OllamaConfig, EndpointConfig, ServingBackend
from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OllamaModel:
    """Information about an Ollama model."""
    name: str
    size: int
    digest: str
    modified_at: str
    details: Dict[str, Any] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "OllamaModel":
        return cls(
            name=data.get("name", ""),
            size=data.get("size", 0),
            digest=data.get("digest", ""),
            modified_at=data.get("modified_at", ""),
            details=data.get("details", {}),
        )


@dataclass
class DeploymentResult:
    """Result of a model deployment."""
    success: bool
    model_name: str
    error: Optional[str] = None
    endpoint: Optional[str] = None
    details: Dict[str, Any] = None


class OllamaBackend:
    """
    Enhanced Ollama backend for model deployment.
    
    Features:
    - Deploy custom models from HuggingFace format
    - Automatic GGUF conversion
    - Modelfile generation
    - Model management (list, delete, copy)
    - Health monitoring
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        Initialize the Ollama backend.
        
        Args:
            config: Ollama configuration
        """
        self.config = config or OllamaConfig()
        self._client = None
        self._exporter = ModelExporter()
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=120.0,  # Long timeout for model operations
            )
        return self._client
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> List[OllamaModel]:
        """List all Ollama models."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            
            data = response.json()
            return [OllamaModel.from_api(m) for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def model_exists(self, model_name: str) -> bool:
        """Check if a model exists."""
        models = await self.list_models()
        return any(m.name == model_name for m in models)
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        try:
            response = await self.client.post(
                "/api/show",
                json={"name": model_name},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
    
    async def deploy_custom_model(
        self,
        model_path: str,
        model_name: str,
        quantization: Optional[str] = None,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """
        Deploy a custom model to Ollama.
        
        Args:
            model_path: Path to the model (HuggingFace format or GGUF)
            model_name: Name for the Ollama model
            quantization: GGUF quantization type (q4_k_m, q5_k_m, etc.)
            system_prompt: Default system prompt
            template: Chat template
            parameters: Model parameters
        
        Returns:
            DeploymentResult
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            return DeploymentResult(
                success=False,
                model_name=model_name,
                error=f"Model path does not exist: {model_path}",
            )
        
        try:
            # Check for existing GGUF file
            gguf_files = list(model_path.glob("*.gguf"))
            
            if not gguf_files:
                # Convert to GGUF
                logger.info(f"Converting model to GGUF format...")
                quant = quantization or self.config.default_quantization
                
                export_config = ExportConfig(
                    format=ExportFormat.GGUF,
                    output_dir=str(model_path / "gguf"),
                    gguf_quantization=quant,
                )
                
                result = self._exporter.export(str(model_path), export_config)
                
                if not result.success:
                    return DeploymentResult(
                        success=False,
                        model_name=model_name,
                        error=f"GGUF conversion failed: {result.error}",
                    )
                
                gguf_path = result.output_path
            else:
                gguf_path = str(gguf_files[0])
            
            # Generate Modelfile
            modelfile = self._generate_modelfile(
                gguf_path=gguf_path,
                system_prompt=system_prompt,
                template=template,
                parameters=parameters,
            )
            
            # Create model in Ollama
            logger.info(f"Creating Ollama model: {model_name}")
            response = await self.client.post(
                "/api/create",
                json={
                    "name": model_name,
                    "modelfile": modelfile,
                },
                timeout=600.0,  # 10 minute timeout for model creation
            )
            
            if response.status_code != 200:
                return DeploymentResult(
                    success=False,
                    model_name=model_name,
                    error=f"Ollama create failed: {response.text}",
                )
            
            # Verify model was created
            if await self.model_exists(model_name):
                return DeploymentResult(
                    success=True,
                    model_name=model_name,
                    endpoint=f"ollama run {model_name}",
                    details={
                        "gguf_path": gguf_path,
                        "modelfile": modelfile,
                    },
                )
            else:
                return DeploymentResult(
                    success=False,
                    model_name=model_name,
                    error="Model creation succeeded but model not found",
                )
                
        except Exception as e:
            logger.exception(f"Failed to deploy model: {e}")
            return DeploymentResult(
                success=False,
                model_name=model_name,
                error=str(e),
            )
    
    def _generate_modelfile(
        self,
        gguf_path: str,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate an Ollama Modelfile."""
        lines = [f"FROM {gguf_path}"]
        
        # Add parameters
        params = parameters or {}
        params.setdefault("temperature", self.config.temperature)
        params.setdefault("top_p", self.config.top_p)
        params.setdefault("top_k", self.config.top_k)
        params.setdefault("num_ctx", self.config.num_ctx)
        
        for key, value in params.items():
            lines.append(f"PARAMETER {key} {value}")
        
        # Add template
        if template:
            lines.append(f'TEMPLATE """{template}"""')
        
        # Add system prompt
        if system_prompt:
            lines.append(f'SYSTEM """{system_prompt}"""')
        else:
            lines.append('SYSTEM """You are a helpful AI assistant."""')
        
        return "\n".join(lines)
    
    async def deploy_from_gguf(
        self,
        gguf_path: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResult:
        """
        Deploy a model directly from a GGUF file.
        
        Args:
            gguf_path: Path to GGUF file
            model_name: Name for the Ollama model
            system_prompt: Default system prompt
            parameters: Model parameters
        
        Returns:
            DeploymentResult
        """
        if not Path(gguf_path).exists():
            return DeploymentResult(
                success=False,
                model_name=model_name,
                error=f"GGUF file not found: {gguf_path}",
            )
        
        try:
            modelfile = self._generate_modelfile(
                gguf_path=gguf_path,
                system_prompt=system_prompt,
                parameters=parameters,
            )
            
            response = await self.client.post(
                "/api/create",
                json={
                    "name": model_name,
                    "modelfile": modelfile,
                },
                timeout=600.0,
            )
            
            if response.status_code == 200:
                return DeploymentResult(
                    success=True,
                    model_name=model_name,
                    endpoint=f"ollama run {model_name}",
                )
            else:
                return DeploymentResult(
                    success=False,
                    model_name=model_name,
                    error=response.text,
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                model_name=model_name,
                error=str(e),
            )
    
    async def copy_model(self, source: str, destination: str) -> bool:
        """Copy an existing model."""
        try:
            response = await self.client.post(
                "/api/copy",
                json={"source": source, "destination": destination},
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to copy model: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model."""
        try:
            response = await self.client.delete(
                "/api/delete",
                json={"name": model_name},
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = await self.client.post(
                "/api/pull",
                json={"name": model_name},
                timeout=3600.0,  # 1 hour for large models
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama.
        
        Args:
            model: Model name
            prompt: Input prompt
            system: System prompt
            temperature: Temperature
            max_tokens: Maximum tokens
            stream: Stream response
        
        Returns:
            Generation result
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        
        if system:
            payload["system"] = system
        
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        
        if options:
            payload["options"] = options
        
        try:
            response = await self.client.post(
                "/api/generate",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {"error": str(e)}
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Chat completion using Ollama.
        
        Args:
            model: Model name
            messages: Chat messages
            temperature: Temperature
            max_tokens: Maximum tokens
        
        Returns:
            Chat response
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        
        if options:
            payload["options"] = options
        
        try:
            response = await self.client.post(
                "/api/chat",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the client."""
        if self._client:
            await self._client.aclose()
            self._client = None
