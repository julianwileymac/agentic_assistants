"""
Model export utilities.

This module provides utilities for exporting trained models to various formats
including GGUF, SafeTensors, and HuggingFace format.
"""

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ExportFormat(str, Enum):
    """Supported model export formats."""
    HUGGINGFACE = "huggingface"   # Standard HF format
    SAFETENSORS = "safetensors"  # SafeTensors format
    GGUF = "gguf"                 # GGUF for llama.cpp / Ollama
    GGML = "ggml"                 # Legacy GGML format
    PYTORCH = "pytorch"          # PyTorch .pt files
    ONNX = "onnx"                 # ONNX format


@dataclass
class ExportConfig:
    """Configuration for model export."""
    
    format: ExportFormat
    output_dir: str
    
    # GGUF-specific options
    gguf_quantization: Optional[str] = None  # Q4_K_M, Q5_K_M, Q8_0, etc.
    gguf_vocab_type: Optional[str] = None
    
    # SafeTensors options
    merge_lora: bool = True  # Merge LoRA weights before export
    
    # General options
    include_tokenizer: bool = True
    include_config: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format.value,
            "output_dir": self.output_dir,
            "gguf_quantization": self.gguf_quantization,
            "gguf_vocab_type": self.gguf_vocab_type,
            "merge_lora": self.merge_lora,
            "include_tokenizer": self.include_tokenizer,
            "include_config": self.include_config,
        }


@dataclass
class ExportResult:
    """Result of a model export operation."""
    
    success: bool
    output_path: str
    format: ExportFormat
    size_bytes: int = 0
    error: Optional[str] = None
    
    # Additional metadata
    quantization: Optional[str] = None
    model_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.model_info is None:
            self.model_info = {}


class ModelExporter:
    """
    Export models to various formats.
    
    Supports exporting trained models to GGUF (for Ollama/llama.cpp),
    SafeTensors, and other formats.
    """
    
    def __init__(self):
        """Initialize the model exporter."""
        self._check_dependencies()
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check which export dependencies are available."""
        deps = {
            "llama_cpp": False,
            "transformers": False,
            "safetensors": False,
            "onnx": False,
        }
        
        try:
            import llama_cpp
            deps["llama_cpp"] = True
        except ImportError:
            pass
        
        try:
            import transformers
            deps["transformers"] = True
        except ImportError:
            pass
        
        try:
            import safetensors
            deps["safetensors"] = True
        except ImportError:
            pass
        
        try:
            import onnx
            deps["onnx"] = True
        except ImportError:
            pass
        
        return deps
    
    def export(
        self,
        model_path: str,
        config: ExportConfig,
    ) -> ExportResult:
        """
        Export a model to the specified format.
        
        Args:
            model_path: Path to the source model
            config: Export configuration
        
        Returns:
            ExportResult with status and output path
        """
        model_path = Path(model_path)
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting model from {model_path} to {config.format.value}")
        
        try:
            if config.format == ExportFormat.GGUF:
                return self._export_gguf(model_path, config)
            elif config.format == ExportFormat.SAFETENSORS:
                return self._export_safetensors(model_path, config)
            elif config.format == ExportFormat.HUGGINGFACE:
                return self._export_huggingface(model_path, config)
            elif config.format == ExportFormat.PYTORCH:
                return self._export_pytorch(model_path, config)
            else:
                return ExportResult(
                    success=False,
                    output_path="",
                    format=config.format,
                    error=f"Unsupported export format: {config.format}",
                )
        except Exception as e:
            logger.exception(f"Export failed: {e}")
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=config.format,
                error=str(e),
            )
    
    def _export_gguf(
        self,
        model_path: Path,
        config: ExportConfig,
    ) -> ExportResult:
        """Export model to GGUF format."""
        output_dir = Path(config.output_dir)
        
        # Check for llama.cpp convert script
        # First try to use llama-cpp-python if available
        try:
            from llama_cpp import Llama
            has_llama_cpp = True
        except ImportError:
            has_llama_cpp = False
        
        # Determine output filename
        quant_suffix = config.gguf_quantization or "f16"
        model_name = model_path.name
        output_filename = f"{model_name}-{quant_suffix}.gguf"
        output_path = output_dir / output_filename
        
        # Try using the convert script from llama.cpp
        # This typically requires llama.cpp to be installed
        convert_script = self._find_convert_script()
        
        if convert_script:
            # Use llama.cpp conversion script
            cmd = [
                "python", str(convert_script),
                str(model_path),
                "--outfile", str(output_path),
                "--outtype", quant_suffix.lower(),
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600,  # 1 hour timeout
                )
                
                if result.returncode != 0:
                    return ExportResult(
                        success=False,
                        output_path=str(output_path),
                        format=ExportFormat.GGUF,
                        error=f"Conversion failed: {result.stderr}",
                    )
            except subprocess.TimeoutExpired:
                return ExportResult(
                    success=False,
                    output_path=str(output_path),
                    format=ExportFormat.GGUF,
                    error="Conversion timed out",
                )
            except Exception as e:
                return ExportResult(
                    success=False,
                    output_path=str(output_path),
                    format=ExportFormat.GGUF,
                    error=str(e),
                )
        else:
            # Fallback: Try using transformers + ctransformers approach
            logger.warning("llama.cpp convert script not found. Using fallback method.")
            
            # Create a placeholder for manual conversion
            placeholder = output_dir / "CONVERSION_REQUIRED.txt"
            with open(placeholder, "w") as f:
                f.write(f"Manual GGUF conversion required.\n")
                f.write(f"Source model: {model_path}\n")
                f.write(f"Target quantization: {quant_suffix}\n")
                f.write(f"\nTo convert manually:\n")
                f.write(f"1. Install llama.cpp\n")
                f.write(f"2. Run: python convert.py {model_path} --outfile {output_path} --outtype {quant_suffix}\n")
            
            return ExportResult(
                success=False,
                output_path=str(output_path),
                format=ExportFormat.GGUF,
                error="GGUF conversion requires llama.cpp. See CONVERSION_REQUIRED.txt",
                model_info={"placeholder": str(placeholder)},
            )
        
        # Calculate output size
        size_bytes = output_path.stat().st_size if output_path.exists() else 0
        
        return ExportResult(
            success=True,
            output_path=str(output_path),
            format=ExportFormat.GGUF,
            size_bytes=size_bytes,
            quantization=quant_suffix,
            model_info={
                "source_model": str(model_path),
                "quantization": quant_suffix,
            },
        )
    
    def _export_safetensors(
        self,
        model_path: Path,
        config: ExportConfig,
    ) -> ExportResult:
        """Export model to SafeTensors format."""
        output_dir = Path(config.output_dir)
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from safetensors.torch import save_file
            import torch
        except ImportError as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.SAFETENSORS,
                error=f"Missing dependency: {e}",
            )
        
        try:
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                torch_dtype=torch.float16,
                device_map="cpu",
            )
            
            # Merge LoRA weights if requested and applicable
            if config.merge_lora:
                try:
                    from peft import PeftModel
                    if hasattr(model, 'merge_and_unload'):
                        model = model.merge_and_unload()
                        logger.info("Merged LoRA weights into base model")
                except Exception:
                    pass
            
            # Get state dict
            state_dict = model.state_dict()
            
            # Save as SafeTensors
            safetensors_path = output_dir / "model.safetensors"
            save_file(state_dict, str(safetensors_path))
            
            # Copy tokenizer and config
            if config.include_tokenizer:
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                tokenizer.save_pretrained(str(output_dir))
            
            if config.include_config:
                config_file = model_path / "config.json"
                if config_file.exists():
                    shutil.copy(config_file, output_dir / "config.json")
            
            size_bytes = safetensors_path.stat().st_size
            
            return ExportResult(
                success=True,
                output_path=str(safetensors_path),
                format=ExportFormat.SAFETENSORS,
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.SAFETENSORS,
                error=str(e),
            )
    
    def _export_huggingface(
        self,
        model_path: Path,
        config: ExportConfig,
    ) -> ExportResult:
        """Export model to HuggingFace format."""
        output_dir = Path(config.output_dir)
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.HUGGINGFACE,
                error=f"Missing dependency: {e}",
            )
        
        try:
            # Load and save model
            model = AutoModelForCausalLM.from_pretrained(str(model_path))
            
            # Merge LoRA if requested
            if config.merge_lora:
                try:
                    if hasattr(model, 'merge_and_unload'):
                        model = model.merge_and_unload()
                except Exception:
                    pass
            
            model.save_pretrained(str(output_dir))
            
            # Save tokenizer
            if config.include_tokenizer:
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                tokenizer.save_pretrained(str(output_dir))
            
            # Calculate total size
            size_bytes = sum(
                f.stat().st_size 
                for f in output_dir.rglob("*") 
                if f.is_file()
            )
            
            return ExportResult(
                success=True,
                output_path=str(output_dir),
                format=ExportFormat.HUGGINGFACE,
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.HUGGINGFACE,
                error=str(e),
            )
    
    def _export_pytorch(
        self,
        model_path: Path,
        config: ExportConfig,
    ) -> ExportResult:
        """Export model to PyTorch format."""
        output_dir = Path(config.output_dir)
        
        try:
            from transformers import AutoModelForCausalLM
            import torch
        except ImportError as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.PYTORCH,
                error=f"Missing dependency: {e}",
            )
        
        try:
            model = AutoModelForCausalLM.from_pretrained(str(model_path))
            
            output_file = output_dir / "model.pt"
            torch.save(model.state_dict(), str(output_file))
            
            size_bytes = output_file.stat().st_size
            
            return ExportResult(
                success=True,
                output_path=str(output_file),
                format=ExportFormat.PYTORCH,
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                output_path=str(output_dir),
                format=ExportFormat.PYTORCH,
                error=str(e),
            )
    
    def _find_convert_script(self) -> Optional[Path]:
        """Find llama.cpp convert script."""
        # Common locations
        possible_paths = [
            Path("llama.cpp/convert.py"),
            Path("./convert.py"),
            Path.home() / "llama.cpp" / "convert.py",
            Path("/opt/llama.cpp/convert.py"),
        ]
        
        # Check environment variable
        llama_cpp_path = os.environ.get("LLAMA_CPP_PATH")
        if llama_cpp_path:
            possible_paths.insert(0, Path(llama_cpp_path) / "convert.py")
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def get_supported_formats(self) -> List[ExportFormat]:
        """Get list of supported export formats based on available dependencies."""
        deps = self._check_dependencies()
        supported = []
        
        if deps["transformers"]:
            supported.extend([
                ExportFormat.HUGGINGFACE,
                ExportFormat.PYTORCH,
            ])
        
        if deps["transformers"] and deps["safetensors"]:
            supported.append(ExportFormat.SAFETENSORS)
        
        if deps["llama_cpp"] or self._find_convert_script():
            supported.append(ExportFormat.GGUF)
        
        return supported
    
    def get_gguf_quantizations(self) -> List[str]:
        """Get list of supported GGUF quantization types."""
        return [
            "f32",      # Full precision
            "f16",      # Half precision
            "q8_0",     # 8-bit quantization
            "q6_k",     # 6-bit k-quant
            "q5_k_m",   # 5-bit k-quant medium
            "q5_k_s",   # 5-bit k-quant small
            "q4_k_m",   # 4-bit k-quant medium
            "q4_k_s",   # 4-bit k-quant small
            "q3_k_m",   # 3-bit k-quant medium
            "q3_k_s",   # 3-bit k-quant small
            "q2_k",     # 2-bit k-quant
            "iq4_nl",   # 4-bit i-quant
            "iq3_xxs",  # 3-bit i-quant extra extra small
        ]
