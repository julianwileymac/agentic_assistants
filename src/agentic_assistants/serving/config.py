"""
Model serving configuration.

This module defines configuration classes for model serving backends.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ServingBackend(str, Enum):
    """Supported serving backends."""
    OLLAMA = "ollama"
    VLLM = "vllm"
    TGI = "tgi"
    LOCAL = "local"  # Direct transformers inference


@dataclass
class EndpointConfig:
    """Configuration for a model endpoint."""
    
    name: str
    model_id: str
    backend: ServingBackend
    host: str = "localhost"
    port: int = 8000
    
    # Model settings
    max_batch_size: int = 32
    max_sequence_length: int = 4096
    
    # Resource settings
    gpu_memory_utilization: float = 0.9
    num_gpus: int = 1
    
    # Health check
    health_check_path: str = "/health"
    
    # Status
    status: str = "stopped"  # stopped, starting, running, error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_id": self.model_id,
            "backend": self.backend.value,
            "host": self.host,
            "port": self.port,
            "max_batch_size": self.max_batch_size,
            "max_sequence_length": self.max_sequence_length,
            "gpu_memory_utilization": self.gpu_memory_utilization,
            "num_gpus": self.num_gpus,
            "status": self.status,
        }


class OllamaConfig(BaseModel):
    """Configuration for Ollama backend."""
    
    host: str = Field(default="localhost", description="Ollama host")
    port: int = Field(default=11434, description="Ollama port")
    
    # Model creation settings
    num_ctx: int = Field(default=4096, description="Context window size")
    num_gpu: int = Field(default=-1, description="Number of GPUs (-1 for auto)")
    num_thread: int = Field(default=-1, description="Number of threads (-1 for auto)")
    
    # Default parameters
    temperature: float = Field(default=0.7, description="Default temperature")
    top_p: float = Field(default=0.9, description="Default top_p")
    top_k: int = Field(default=40, description="Default top_k")
    
    # Quantization defaults
    default_quantization: str = Field(default="q4_k_m", description="Default GGUF quantization")
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    class Config:
        extra = "allow"


class VLLMConfig(BaseModel):
    """Configuration for vLLM backend."""
    
    host: str = Field(default="localhost", description="vLLM host")
    port: int = Field(default=8000, description="vLLM port")
    
    # Model settings
    tensor_parallel_size: int = Field(default=1, description="Tensor parallelism")
    gpu_memory_utilization: float = Field(default=0.9, description="GPU memory utilization")
    max_model_len: Optional[int] = Field(None, description="Maximum model length")
    
    # Serving settings
    max_num_seqs: int = Field(default=256, description="Maximum concurrent sequences")
    max_num_batched_tokens: Optional[int] = Field(None, description="Max batched tokens")
    
    # API settings
    api_key: Optional[str] = Field(None, description="API key for authentication")
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/v1"
    
    class Config:
        extra = "allow"


class TGIConfig(BaseModel):
    """Configuration for Text Generation Inference backend."""
    
    host: str = Field(default="localhost", description="TGI host")
    port: int = Field(default=8080, description="TGI port")
    
    # Model settings
    max_input_length: int = Field(default=1024, description="Max input length")
    max_total_tokens: int = Field(default=2048, description="Max total tokens")
    max_batch_prefill_tokens: int = Field(default=4096, description="Max batch prefill tokens")
    
    # Quantization
    quantize: Optional[str] = Field(None, description="Quantization: bitsandbytes, gptq, awq")
    
    # Hardware
    num_shard: int = Field(default=1, description="Number of shards")
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    class Config:
        extra = "allow"


class ServingConfig(BaseModel):
    """Main serving configuration."""
    
    # Backend-specific configs
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    vllm: VLLMConfig = Field(default_factory=VLLMConfig)
    tgi: TGIConfig = Field(default_factory=TGIConfig)
    
    # Default backend
    default_backend: ServingBackend = Field(
        default=ServingBackend.OLLAMA,
        description="Default serving backend"
    )
    
    # Auto-start settings
    auto_start: bool = Field(default=False, description="Auto-start endpoints on load")
    
    # Health check interval
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    class Config:
        extra = "allow"
