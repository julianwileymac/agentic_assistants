"""
Nemotron model integration.

Provides model weight fetching, loading, serving, export, and MLFlow
registration for NVIDIA Nemotron-Nano model family.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

NEMOTRON_MODELS = {
    "nemotron-nano-8b": "nvidia/Llama-3.1-Nemotron-Nano-8B-v1",
    "nemotron-mini-4b": "nvidia/Nemotron-Mini-4B-Instruct",
}

DEFAULT_MODEL = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"


class NemotronModelConfig(BaseModel):
    """Configuration for loading a nemotron model."""
    model_id: str = Field(default=DEFAULT_MODEL)
    revision: str = Field(default="main")
    quantization: str = Field(default="none", description="none, int8, int4, gptq, awq")
    device_map: str = Field(default="auto")
    torch_dtype: str = Field(default="bfloat16")
    trust_remote_code: bool = Field(default=True)
    max_memory: Optional[Dict[str, str]] = None
    attn_implementation: Optional[str] = Field(
        default=None, description="eager, sdpa, or flash_attention_2"
    )


@dataclass
class ModelInfo:
    """Metadata about a downloaded/loaded model."""
    model_id: str
    local_path: str
    parameter_count: Optional[int] = None
    estimated_memory_gb: Optional[float] = None
    quantization: str = "none"
    status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


class NemotronModelManager:
    """
    Manages nemotron model lifecycle: fetch, load, serve, export.

    Integrates with the framework's HuggingFace, PyTorch, serving,
    training, and MLFlow subsystems.

    Example:
        >>> mgr = NemotronModelManager()
        >>> mgr.fetch_weights("nvidia/Llama-3.1-Nemotron-Nano-8B-v1")
        >>> mgr.deploy("nemotron-nano-coding", backend="ollama")
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        default_model: str = DEFAULT_MODEL,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./data/models")
        self.default_model = default_model
        self._loaded_models: Dict[str, Any] = {}
        self._model_infos: Dict[str, ModelInfo] = {}

    def fetch_weights(
        self,
        model_id: Optional[str] = None,
        revision: str = "main",
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Download model weights from HuggingFace Hub.

        Uses the framework's HuggingFaceHubIntegration when available,
        falls back to huggingface_hub directly.
        """
        model_id = model_id or self.default_model
        local_dir = self.cache_dir / model_id.replace("/", "--")
        local_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Fetching weights for {model_id} (revision: {revision})")
        start = time.time()

        try:
            from agentic_assistants.integrations.huggingface import HuggingFaceHubIntegration
            hf = HuggingFaceHubIntegration()
            result = hf.pull_model(
                repo_id=model_id,
                local_dir=str(local_dir),
                revision=revision,
            )
            elapsed = time.time() - start
            info = ModelInfo(
                model_id=model_id,
                local_path=str(local_dir),
                status="downloaded",
                metadata={"revision": revision, "download_time_s": elapsed},
            )
            self._model_infos[model_id] = info
            logger.info(f"Model downloaded to {local_dir} in {elapsed:.1f}s")
            return {"model_id": model_id, "local_path": str(local_dir), "status": "downloaded"}

        except Exception:
            logger.info("Framework HF integration unavailable, using huggingface_hub directly")

        try:
            from huggingface_hub import snapshot_download
            path = snapshot_download(
                repo_id=model_id,
                revision=revision,
                local_dir=str(local_dir),
                token=token,
            )
            elapsed = time.time() - start
            info = ModelInfo(
                model_id=model_id,
                local_path=str(path),
                status="downloaded",
                metadata={"revision": revision, "download_time_s": elapsed},
            )
            self._model_infos[model_id] = info
            logger.info(f"Model downloaded to {path} in {elapsed:.1f}s")
            return {"model_id": model_id, "local_path": str(path), "status": "downloaded"}

        except ImportError:
            return {"model_id": model_id, "status": "error", "error": "huggingface_hub not installed"}
        except Exception as e:
            logger.error(f"Failed to fetch {model_id}: {e}")
            return {"model_id": model_id, "status": "error", "error": str(e)}

    def load_model(
        self,
        config: Optional[NemotronModelConfig] = None,
        model_path: Optional[str] = None,
    ) -> Any:
        """
        Load the model into memory with appropriate dtype and quantization.
        """
        config = config or NemotronModelConfig()
        model_id = model_path or config.model_id
        cache_key = f"{model_id}:{config.quantization}"

        if cache_key in self._loaded_models:
            return self._loaded_models[cache_key]

        try:
            from agentic_assistants.integrations.pytorch_utils import (
                get_device, get_dtype_for_device, is_cuda_available,
            )
        except ImportError:
            get_device = lambda: "cpu"
            get_dtype_for_device = lambda d: "float32"
            is_cuda_available = lambda: False

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            dtype_map = {
                "bfloat16": torch.bfloat16,
                "float16": torch.float16,
                "float32": torch.float32,
            }
            torch_dtype = dtype_map.get(config.torch_dtype, torch.bfloat16)

            load_kwargs: Dict[str, Any] = {
                "torch_dtype": torch_dtype,
                "device_map": config.device_map,
                "trust_remote_code": config.trust_remote_code,
            }

            if config.attn_implementation:
                load_kwargs["attn_implementation"] = config.attn_implementation

            if config.quantization == "int4":
                from transformers import BitsAndBytesConfig
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch_dtype,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            elif config.quantization == "int8":
                from transformers import BitsAndBytesConfig
                load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)

            logger.info(f"Loading model {model_id} (quantization={config.quantization})")
            model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, trust_remote_code=config.trust_remote_code,
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            self._loaded_models[cache_key] = {"model": model, "tokenizer": tokenizer}

            param_count = sum(p.numel() for p in model.parameters())
            self._model_infos[model_id] = ModelInfo(
                model_id=model_id,
                local_path=model_id,
                parameter_count=param_count,
                quantization=config.quantization,
                status="loaded",
            )

            logger.info(f"Model loaded: {param_count:,} parameters")
            return self._loaded_models[cache_key]

        except ImportError as e:
            logger.error(f"Missing dependency for model loading: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def register_with_mlflow(
        self,
        model_path: str,
        experiment_name: str = "nemotron-coding-assistant",
        model_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register a model with MLFlow tracking."""
        try:
            from agentic_assistants.training.mlflow_integration import TrainingMLFlowIntegration
            mlflow_int = TrainingMLFlowIntegration()
            result = mlflow_int.register_model(
                model_path=model_path,
                model_name=model_name or "nemotron-nano-coding",
                experiment_name=experiment_name,
                tags=tags or {"model_family": "nemotron-nano"},
            )
            return {"status": "registered", "result": result}
        except Exception as e:
            logger.error(f"MLFlow registration failed: {e}")
            return {"status": "error", "error": str(e)}

    def export_to_ollama(
        self,
        model_path: str,
        model_name: str = "nemotron-nano-coding",
    ) -> Dict[str, Any]:
        """Export and register model with Ollama."""
        try:
            from agentic_assistants.training.ollama_export import OllamaModelExporter
            exporter = OllamaModelExporter()
            result = exporter.export(
                model_path=model_path,
                model_name=model_name,
            )
            return {"status": "exported", "model_name": model_name, "result": result}
        except Exception as e:
            logger.error(f"Ollama export failed: {e}")
            return {"status": "error", "error": str(e)}

    def export(
        self,
        model_path: str,
        format: str = "gguf",
        quantization: str = "q4_k_m",
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Export model to specified format (GGUF, SafeTensors, etc.)."""
        output_dir = output_dir or str(self.cache_dir / "exports")
        try:
            from agentic_assistants.training.export import ModelExporter
            exporter = ModelExporter()
            result = exporter.export(
                model_path=model_path,
                format=format,
                quantization=quantization,
                output_dir=output_dir,
            )
            return {"status": "exported", "format": format, "result": result}
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {"status": "error", "error": str(e)}

    def deploy(
        self,
        model_path: str,
        backend: str = "ollama",
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploy model for inference via the serving manager."""
        model_name = model_name or "nemotron-nano-coding"
        try:
            from agentic_assistants.serving.manager import ServingManager
            mgr = ServingManager()
            result = mgr.deploy(
                model_path=model_path,
                model_name=model_name,
                backend=backend,
            )
            return {"status": "deployed", "backend": backend, "model_name": model_name}
        except Exception as e:
            logger.error(f"Deploy failed: {e}")
            return {"status": "error", "error": str(e)}

    def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Send a chat request to the served model."""
        model = model or "nemotron-nano-coding"
        try:
            import httpx
            response = httpx.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {"temperature": temperature},
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            return f"Error: {e}"

    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get metadata about a model."""
        model_id = model_id or self.default_model
        info = self._model_infos.get(model_id)
        if info:
            return {
                "model_id": info.model_id,
                "local_path": info.local_path,
                "parameter_count": info.parameter_count,
                "estimated_memory_gb": info.estimated_memory_gb,
                "quantization": info.quantization,
                "status": info.status,
            }

        try:
            from agentic_assistants.integrations.pytorch_utils import estimate_model_memory
            mem = estimate_model_memory(model_id)
            return {"model_id": model_id, "estimated_memory_gb": mem, "status": "not_loaded"}
        except Exception:
            return {"model_id": model_id, "status": "not_loaded"}

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List known nemotron model variants."""
        models = []
        for short_name, model_id in NEMOTRON_MODELS.items():
            info = self._model_infos.get(model_id)
            models.append({
                "short_name": short_name,
                "model_id": model_id,
                "status": info.status if info else "not_downloaded",
            })
        return models
