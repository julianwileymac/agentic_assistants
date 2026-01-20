"""
Ollama Model Import Pipeline.

This module provides functionality to import models from Ollama
for fine-tuning, including:
- Detecting available Ollama models
- Exporting model weights
- Converting to HuggingFace format
- Preparing for fine-tuning

Example:
    >>> from agentic_assistants.training import OllamaModelImporter
    >>> 
    >>> importer = OllamaModelImporter()
    >>> 
    >>> # List available models
    >>> models = await importer.list_available_models()
    >>> 
    >>> # Import a model for fine-tuning
    >>> imported = await importer.import_model("llama3.2", output_path="./models")
"""

import asyncio
import hashlib
import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OllamaModelInfo:
    """Information about an Ollama model."""
    name: str
    tag: str
    size: int
    digest: str
    modified_at: str
    quantization: Optional[str] = None
    family: Optional[str] = None
    parameter_size: Optional[str] = None
    format: str = "gguf"
    
    @property
    def full_name(self) -> str:
        """Get the full model name with tag."""
        return f"{self.name}:{self.tag}" if self.tag else self.name
    
    @property
    def size_gb(self) -> float:
        """Get model size in GB."""
        return self.size / (1024 ** 3)
    
    @classmethod
    def from_ollama_api(cls, data: Dict[str, Any]) -> "OllamaModelInfo":
        """Create from Ollama API response."""
        name_parts = data.get("name", "").split(":")
        name = name_parts[0]
        tag = name_parts[1] if len(name_parts) > 1 else "latest"
        
        details = data.get("details", {})
        
        return cls(
            name=name,
            tag=tag,
            size=data.get("size", 0),
            digest=data.get("digest", ""),
            modified_at=data.get("modified_at", ""),
            quantization=details.get("quantization_level"),
            family=details.get("family"),
            parameter_size=details.get("parameter_size"),
            format=details.get("format", "gguf"),
        )


@dataclass
class ImportedModel:
    """Information about an imported model."""
    name: str
    source_model: str
    output_path: Path
    format: str
    size_bytes: int
    imported_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_convertible(self) -> bool:
        """Check if the model can be converted to HF format."""
        return self.format.lower() in ["gguf", "ggml"]


class OllamaModelImporter:
    """
    Import Ollama models for fine-tuning.
    
    This class handles:
    - Listing available Ollama models
    - Exporting model files from Ollama storage
    - Converting GGUF models to HuggingFace format
    - Preparing models for fine-tuning
    
    Attributes:
        config: Framework configuration
        ollama_host: Ollama server URL
        models_dir: Default directory for imported models
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        models_dir: Optional[Path] = None,
    ):
        """
        Initialize the Ollama model importer.
        
        Args:
            config: Configuration instance
            models_dir: Directory to store imported models
        """
        self.config = config or AgenticConfig()
        self.ollama_host = self.config.ollama.host
        self.models_dir = models_dir or Path("./data/models/imported")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._client = httpx.AsyncClient(timeout=300.0)
    
    async def list_available_models(self) -> List[OllamaModelInfo]:
        """
        List all available Ollama models.
        
        Returns:
            List of model information
        """
        try:
            response = await self._client.get(f"{self.ollama_host}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model_data in data.get("models", []):
                # Get detailed info
                try:
                    detail_response = await self._client.post(
                        f"{self.ollama_host}/api/show",
                        json={"name": model_data.get("name")},
                    )
                    if detail_response.status_code == 200:
                        details = detail_response.json()
                        model_data["details"] = details.get("details", {})
                except Exception:
                    pass
                
                models.append(OllamaModelInfo.from_ollama_api(model_data))
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def get_model_info(self, model_name: str) -> Optional[OllamaModelInfo]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information or None if not found
        """
        try:
            response = await self._client.post(
                f"{self.ollama_host}/api/show",
                json={"name": model_name},
            )
            response.raise_for_status()
            data = response.json()
            
            # Build model info
            return OllamaModelInfo(
                name=model_name.split(":")[0],
                tag=model_name.split(":")[1] if ":" in model_name else "latest",
                size=0,  # Not in show response
                digest=data.get("digest", ""),
                modified_at=data.get("modified_at", ""),
                quantization=data.get("details", {}).get("quantization_level"),
                family=data.get("details", {}).get("family"),
                parameter_size=data.get("details", {}).get("parameter_size"),
                format=data.get("details", {}).get("format", "gguf"),
            )
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return None
    
    def _get_ollama_models_path(self) -> Optional[Path]:
        """Get the Ollama models storage path."""
        system = platform.system()
        
        if system == "Windows":
            # Windows: %USERPROFILE%\.ollama\models
            home = os.environ.get("USERPROFILE", "")
            return Path(home) / ".ollama" / "models"
        elif system == "Darwin":
            # macOS: ~/.ollama/models
            return Path.home() / ".ollama" / "models"
        else:
            # Linux: ~/.ollama/models
            return Path.home() / ".ollama" / "models"
    
    def _find_model_blob(self, model_name: str) -> Optional[Path]:
        """Find the model blob file."""
        ollama_path = self._get_ollama_models_path()
        if not ollama_path or not ollama_path.exists():
            return None
        
        # Look in blobs directory
        blobs_path = ollama_path / "blobs"
        if not blobs_path.exists():
            return None
        
        # Get the manifest to find the correct blob
        manifests_path = ollama_path / "manifests" / "registry.ollama.ai" / "library"
        
        # Parse model name and tag
        parts = model_name.split(":")
        name = parts[0]
        tag = parts[1] if len(parts) > 1 else "latest"
        
        manifest_file = manifests_path / name / tag
        if not manifest_file.exists():
            # Try without the library path
            manifest_file = ollama_path / "manifests" / name / tag
        
        if manifest_file.exists():
            try:
                with open(manifest_file, "r") as f:
                    manifest = json.load(f)
                
                # Find the model layer
                for layer in manifest.get("layers", []):
                    if layer.get("mediaType") == "application/vnd.ollama.image.model":
                        digest = layer.get("digest", "").replace(":", "-")
                        blob_file = blobs_path / digest
                        if blob_file.exists():
                            return blob_file
            except Exception as e:
                logger.warning(f"Failed to parse manifest: {e}")
        
        # Fallback: look for any large blob file
        for blob_file in blobs_path.glob("*"):
            if blob_file.is_file() and blob_file.stat().st_size > 100_000_000:  # > 100MB
                return blob_file
        
        return None
    
    async def import_model(
        self,
        model_name: str,
        output_path: Optional[Path] = None,
        copy_weights: bool = True,
    ) -> Optional[ImportedModel]:
        """
        Import a model from Ollama for fine-tuning.
        
        Args:
            model_name: Name of the Ollama model
            output_path: Where to store the imported model
            copy_weights: Whether to copy (True) or link (False) the weights
            
        Returns:
            ImportedModel if successful, None otherwise
        """
        logger.info(f"Importing Ollama model: {model_name}")
        
        # Get model info
        model_info = await self.get_model_info(model_name)
        if not model_info:
            logger.error(f"Model not found: {model_name}")
            return None
        
        # Determine output path
        output_path = output_path or self.models_dir / model_name.replace(":", "_")
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find the model blob
        blob_path = self._find_model_blob(model_name)
        if not blob_path:
            logger.error(f"Could not find model blob for: {model_name}")
            return None
        
        # Copy or link the model file
        output_file = output_path / f"{model_name.replace(':', '_')}.gguf"
        
        if copy_weights:
            logger.info(f"Copying model weights to {output_file}")
            shutil.copy2(blob_path, output_file)
        else:
            logger.info(f"Creating symlink to model at {output_file}")
            if output_file.exists():
                output_file.unlink()
            output_file.symlink_to(blob_path)
        
        # Save metadata
        metadata = {
            "source_model": model_name,
            "family": model_info.family,
            "parameter_size": model_info.parameter_size,
            "quantization": model_info.quantization,
            "format": model_info.format,
            "imported_at": datetime.utcnow().isoformat(),
            "blob_path": str(blob_path),
        }
        
        metadata_file = output_path / "import_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        imported = ImportedModel(
            name=model_name.replace(":", "_"),
            source_model=model_name,
            output_path=output_path,
            format=model_info.format,
            size_bytes=output_file.stat().st_size,
            metadata=metadata,
        )
        
        logger.info(f"Successfully imported model: {imported.name}")
        return imported
    
    async def convert_to_huggingface(
        self,
        imported_model: ImportedModel,
        output_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Convert an imported GGUF model to HuggingFace format.
        
        This requires llama.cpp's convert tools to be available.
        
        Args:
            imported_model: The imported model to convert
            output_path: Where to store the HF model
            
        Returns:
            Path to the converted model, or None if conversion failed
        """
        if not imported_model.is_convertible:
            logger.error(f"Model format {imported_model.format} is not convertible")
            return None
        
        output_path = output_path or imported_model.output_path / "hf_model"
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find the GGUF file
        gguf_files = list(imported_model.output_path.glob("*.gguf"))
        if not gguf_files:
            logger.error("No GGUF file found in imported model")
            return None
        
        gguf_file = gguf_files[0]
        
        # Try to use llama.cpp convert tool
        try:
            # Check for convert script
            convert_script = shutil.which("convert-gguf-to-hf")
            if not convert_script:
                # Try Python-based conversion
                return await self._convert_with_transformers(gguf_file, output_path)
            
            # Run conversion
            result = subprocess.run(
                [convert_script, str(gguf_file), str(output_path)],
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                logger.error(f"Conversion failed: {result.stderr}")
                return None
            
            logger.info(f"Converted model to HuggingFace format at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None
    
    async def _convert_with_transformers(
        self,
        gguf_file: Path,
        output_path: Path,
    ) -> Optional[Path]:
        """Convert using transformers library if available."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Load from GGUF (requires transformers >= 4.35)
            logger.info(f"Loading model from GGUF: {gguf_file}")
            model = AutoModelForCausalLM.from_pretrained(
                str(gguf_file.parent),
                gguf_file=str(gguf_file.name),
                device_map="auto",
                trust_remote_code=True,
            )
            
            # Save in HF format
            logger.info(f"Saving model in HuggingFace format: {output_path}")
            model.save_pretrained(output_path)
            
            return output_path
            
        except ImportError:
            logger.warning("transformers library not available for GGUF conversion")
            return None
        except Exception as e:
            logger.error(f"Transformers conversion failed: {e}")
            return None
    
    async def prepare_for_training(
        self,
        imported_model: ImportedModel,
    ) -> Dict[str, Any]:
        """
        Prepare an imported model for fine-tuning.
        
        Returns configuration for the TrainingJobManager.
        
        Args:
            imported_model: The imported model
            
        Returns:
            Training configuration dictionary
        """
        # Try to convert to HF format first
        hf_path = await self.convert_to_huggingface(imported_model)
        
        if hf_path:
            # Use HF format for training
            return {
                "base_model": str(hf_path),
                "model_type": "local",
                "source": "ollama_import",
                "original_model": imported_model.source_model,
                "metadata": imported_model.metadata,
            }
        else:
            # Fall back to GGUF-compatible training (limited)
            logger.warning(
                "Could not convert to HF format. "
                "Training options may be limited."
            )
            return {
                "base_model": str(imported_model.output_path),
                "model_type": "gguf",
                "source": "ollama_import",
                "original_model": imported_model.source_model,
                "requires_conversion": True,
                "metadata": imported_model.metadata,
            }
    
    async def cleanup(self, imported_model: ImportedModel) -> bool:
        """
        Clean up an imported model.
        
        Args:
            imported_model: The model to clean up
            
        Returns:
            True if cleanup was successful
        """
        try:
            if imported_model.output_path.exists():
                shutil.rmtree(imported_model.output_path)
            logger.info(f"Cleaned up imported model: {imported_model.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")
            return False
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False
