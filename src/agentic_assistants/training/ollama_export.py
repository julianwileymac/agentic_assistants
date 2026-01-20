"""
Ollama Model Export Pipeline.

This module provides functionality to export fine-tuned models
back to Ollama, including:
- Converting HuggingFace models to GGUF format
- Creating Modelfiles with custom configurations
- Registering models with Ollama

Example:
    >>> from agentic_assistants.training import OllamaModelExporter
    >>> 
    >>> exporter = OllamaModelExporter()
    >>> 
    >>> # Export a fine-tuned model to Ollama
    >>> model_name = await exporter.export_model(
    ...     model_path="./models/fine-tuned",
    ...     name="my-custom-model",
    ...     system_prompt="You are a helpful assistant.",
    ... )
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ModelfileConfig:
    """Configuration for an Ollama Modelfile."""
    
    from_model: str
    system_prompt: Optional[str] = None
    template: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    license: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    def to_modelfile(self) -> str:
        """Generate Modelfile content."""
        lines = [f"FROM {self.from_model}"]
        
        if self.system_prompt:
            # Escape quotes in system prompt
            escaped = self.system_prompt.replace('"', '\\"')
            lines.append(f'SYSTEM "{escaped}"')
        
        if self.template:
            lines.append(f'TEMPLATE """{self.template}"""')
        
        for key, value in self.parameters.items():
            lines.append(f"PARAMETER {key} {value}")
        
        if self.license:
            lines.append(f'LICENSE """{self.license}"""')
        
        for message in self.messages:
            role = message.get("role", "user")
            content = message.get("content", "").replace('"', '\\"')
            lines.append(f'MESSAGE {role} "{content}"')
        
        return "\n".join(lines)


@dataclass
class ExportedModel:
    """Information about an exported model."""
    name: str
    source_path: Path
    ollama_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    modelfile_path: Optional[Path] = None
    gguf_path: Optional[Path] = None


class OllamaModelExporter:
    """
    Export models to Ollama.
    
    This class handles:
    - Converting HuggingFace models to GGUF format
    - Creating custom Modelfiles
    - Registering models with Ollama
    - Managing exported models
    
    Attributes:
        config: Framework configuration
        ollama_host: Ollama server URL
        export_dir: Directory for export artifacts
    """
    
    # Default quantization methods in order of preference
    DEFAULT_QUANTIZATIONS = ["q4_k_m", "q4_0", "q8_0", "f16"]
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        export_dir: Optional[Path] = None,
    ):
        """
        Initialize the Ollama model exporter.
        
        Args:
            config: Configuration instance
            export_dir: Directory for export artifacts
        """
        self.config = config or AgenticConfig()
        self.ollama_host = self.config.ollama.host
        self.export_dir = export_dir or Path("./data/models/exported")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self._client = httpx.AsyncClient(timeout=600.0)  # Long timeout for model creation
    
    async def export_model(
        self,
        model_path: Path,
        name: str,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        quantization: str = "q4_k_m",
        base_model: Optional[str] = None,
    ) -> Optional[ExportedModel]:
        """
        Export a model to Ollama.
        
        Args:
            model_path: Path to the model (HF format or GGUF)
            name: Name for the Ollama model
            system_prompt: Custom system prompt
            template: Custom chat template
            parameters: Model parameters (temperature, etc.)
            quantization: Quantization method for conversion
            base_model: Base model for Modelfile (if using existing GGUF)
            
        Returns:
            ExportedModel if successful, None otherwise
        """
        model_path = Path(model_path)
        logger.info(f"Exporting model {name} from {model_path}")
        
        # Determine model format
        is_gguf = any(model_path.glob("*.gguf")) or str(model_path).endswith(".gguf")
        
        if is_gguf:
            # Use existing GGUF
            gguf_path = model_path if model_path.suffix == ".gguf" else next(model_path.glob("*.gguf"))
            logger.info(f"Using existing GGUF file: {gguf_path}")
        else:
            # Convert to GGUF
            logger.info(f"Converting HuggingFace model to GGUF with {quantization} quantization")
            gguf_path = await self.convert_to_gguf(model_path, quantization)
            if not gguf_path:
                logger.error("Failed to convert model to GGUF")
                return None
        
        # Create Modelfile
        modelfile_config = ModelfileConfig(
            from_model=str(gguf_path),
            system_prompt=system_prompt,
            template=template,
            parameters=parameters or {},
        )
        
        # Save Modelfile
        modelfile_path = self.export_dir / f"{name}.Modelfile"
        with open(modelfile_path, "w") as f:
            f.write(modelfile_config.to_modelfile())
        
        logger.info(f"Created Modelfile at {modelfile_path}")
        
        # Create model in Ollama
        ollama_name = await self.create_ollama_model(name, modelfile_path)
        if not ollama_name:
            logger.error("Failed to create model in Ollama")
            return None
        
        exported = ExportedModel(
            name=name,
            source_path=model_path,
            ollama_name=ollama_name,
            modelfile_path=modelfile_path,
            gguf_path=gguf_path,
            metadata={
                "system_prompt": system_prompt,
                "quantization": quantization,
                "parameters": parameters,
            },
        )
        
        # Save export metadata
        metadata_path = self.export_dir / f"{name}_export.json"
        with open(metadata_path, "w") as f:
            json.dump({
                "name": exported.name,
                "source_path": str(exported.source_path),
                "ollama_name": exported.ollama_name,
                "created_at": exported.created_at.isoformat(),
                "metadata": exported.metadata,
                "modelfile_path": str(exported.modelfile_path),
                "gguf_path": str(exported.gguf_path) if exported.gguf_path else None,
            }, f, indent=2)
        
        logger.info(f"Successfully exported model: {ollama_name}")
        return exported
    
    async def convert_to_gguf(
        self,
        model_path: Path,
        quantization: str = "q4_k_m",
        output_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Convert a HuggingFace model to GGUF format.
        
        Requires llama.cpp to be installed.
        
        Args:
            model_path: Path to HuggingFace model
            quantization: Quantization method
            output_path: Output path for GGUF file
            
        Returns:
            Path to the GGUF file, or None if conversion failed
        """
        output_path = output_path or self.export_dir / f"{model_path.name}.gguf"
        
        # Try different conversion methods
        methods = [
            self._convert_with_llama_cpp,
            self._convert_with_transformers,
        ]
        
        for method in methods:
            try:
                result = await method(model_path, output_path, quantization)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Conversion method failed: {e}")
                continue
        
        logger.error("All conversion methods failed")
        return None
    
    async def _convert_with_llama_cpp(
        self,
        model_path: Path,
        output_path: Path,
        quantization: str,
    ) -> Optional[Path]:
        """Convert using llama.cpp tools."""
        # Find llama.cpp convert script
        convert_script = shutil.which("convert.py") or shutil.which("convert-hf-to-gguf.py")
        quantize_tool = shutil.which("quantize") or shutil.which("llama-quantize")
        
        if not convert_script:
            # Try to find in common locations
            possible_paths = [
                Path.home() / "llama.cpp" / "convert.py",
                Path("/opt/llama.cpp/convert.py"),
                Path("C:/llama.cpp/convert.py"),
            ]
            for p in possible_paths:
                if p.exists():
                    convert_script = str(p)
                    break
        
        if not convert_script:
            logger.debug("llama.cpp convert script not found")
            return None
        
        # Convert to f16 GGUF first
        f16_output = output_path.parent / f"{output_path.stem}_f16.gguf"
        
        logger.info(f"Converting to GGUF using llama.cpp: {convert_script}")
        
        result = subprocess.run(
            ["python", convert_script, str(model_path), "--outfile", str(f16_output)],
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            logger.error(f"Conversion failed: {result.stderr}")
            return None
        
        # Quantize if requested and tool is available
        if quantization != "f16" and quantize_tool:
            logger.info(f"Quantizing to {quantization}")
            
            result = subprocess.run(
                [quantize_tool, str(f16_output), str(output_path), quantization],
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                # Clean up f16 file
                f16_output.unlink()
                return output_path
            else:
                logger.warning(f"Quantization failed, using f16: {result.stderr}")
                f16_output.rename(output_path)
                return output_path
        else:
            f16_output.rename(output_path)
            return output_path
    
    async def _convert_with_transformers(
        self,
        model_path: Path,
        output_path: Path,
        quantization: str,
    ) -> Optional[Path]:
        """Convert using transformers/gguf libraries."""
        try:
            # This is a simplified approach - full implementation would use
            # the gguf library directly
            logger.debug("Attempting conversion with transformers")
            
            # Check if we have the required libraries
            try:
                import gguf
            except ImportError:
                logger.debug("gguf library not available")
                return None
            
            # For now, return None as this requires more complex implementation
            # The llama.cpp method is preferred
            return None
            
        except Exception as e:
            logger.debug(f"Transformers conversion failed: {e}")
            return None
    
    async def create_ollama_model(
        self,
        name: str,
        modelfile_path: Path,
    ) -> Optional[str]:
        """
        Create a model in Ollama from a Modelfile.
        
        Args:
            name: Name for the model
            modelfile_path: Path to the Modelfile
            
        Returns:
            Model name if successful, None otherwise
        """
        try:
            # Read the Modelfile
            with open(modelfile_path, "r") as f:
                modelfile_content = f.read()
            
            # Create model via API
            logger.info(f"Creating Ollama model: {name}")
            
            response = await self._client.post(
                f"{self.ollama_host}/api/create",
                json={
                    "name": name,
                    "modelfile": modelfile_content,
                    "stream": False,
                },
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully created Ollama model: {name}")
                return name
            else:
                logger.error(f"Failed to create model: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create Ollama model: {e}")
            return None
    
    async def create_from_base(
        self,
        name: str,
        base_model: str,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Create a new Ollama model from an existing base model.
        
        This is a lightweight way to customize an existing model
        without converting weights.
        
        Args:
            name: Name for the new model
            base_model: Name of the base Ollama model
            system_prompt: Custom system prompt
            template: Custom chat template
            parameters: Model parameters
            
        Returns:
            Model name if successful, None otherwise
        """
        modelfile_config = ModelfileConfig(
            from_model=base_model,
            system_prompt=system_prompt,
            template=template,
            parameters=parameters or {},
        )
        
        # Save Modelfile
        modelfile_path = self.export_dir / f"{name}.Modelfile"
        with open(modelfile_path, "w") as f:
            f.write(modelfile_config.to_modelfile())
        
        return await self.create_ollama_model(name, modelfile_path)
    
    async def delete_model(self, name: str) -> bool:
        """
        Delete a model from Ollama.
        
        Args:
            name: Name of the model to delete
            
        Returns:
            True if successful
        """
        try:
            response = await self._client.delete(
                f"{self.ollama_host}/api/delete",
                json={"name": name},
            )
            
            if response.status_code == 200:
                logger.info(f"Deleted Ollama model: {name}")
                return True
            else:
                logger.error(f"Failed to delete model: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False
    
    async def list_exported_models(self) -> List[Dict[str, Any]]:
        """
        List all exported models.
        
        Returns:
            List of export metadata
        """
        exports = []
        
        for metadata_file in self.export_dir.glob("*_export.json"):
            try:
                with open(metadata_file, "r") as f:
                    exports.append(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to read export metadata: {e}")
        
        return exports
    
    async def cleanup_export(self, name: str) -> bool:
        """
        Clean up export artifacts for a model.
        
        Args:
            name: Name of the exported model
            
        Returns:
            True if cleanup was successful
        """
        try:
            # Remove Modelfile
            modelfile_path = self.export_dir / f"{name}.Modelfile"
            if modelfile_path.exists():
                modelfile_path.unlink()
            
            # Remove metadata
            metadata_path = self.export_dir / f"{name}_export.json"
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Remove GGUF if it was created
            for gguf_file in self.export_dir.glob(f"{name}*.gguf"):
                gguf_file.unlink()
            
            logger.info(f"Cleaned up export artifacts for: {name}")
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


# Convenience function for quick model customization
async def create_custom_ollama_model(
    name: str,
    base_model: str,
    system_prompt: str,
    parameters: Optional[Dict[str, Any]] = None,
    config: Optional[AgenticConfig] = None,
) -> Optional[str]:
    """
    Quickly create a custom Ollama model from an existing base.
    
    Args:
        name: Name for the new model
        base_model: Base Ollama model name
        system_prompt: System prompt for the model
        parameters: Optional model parameters
        config: Configuration instance
        
    Returns:
        Model name if successful
    
    Example:
        >>> model = await create_custom_ollama_model(
        ...     name="my-assistant",
        ...     base_model="llama3.2",
        ...     system_prompt="You are a coding expert."
        ... )
    """
    async with OllamaModelExporter(config) as exporter:
        return await exporter.create_from_base(
            name=name,
            base_model=base_model,
            system_prompt=system_prompt,
            parameters=parameters,
        )
