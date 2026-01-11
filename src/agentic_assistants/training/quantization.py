"""
Model quantization utilities.

This module provides utilities for quantizing trained models using
various quantization methods (GPTQ, AWQ, bitsandbytes).
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.training.config import QuantizationType, QuantizationConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QuantizationResult:
    """Result of a quantization operation."""
    
    success: bool
    output_path: str
    error: Optional[str] = None
    
    original_size_bytes: int = 0
    quantized_size_bytes: int = 0
    compression_ratio: float = 0.0
    
    quantization_type: Optional[str] = None
    bits: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output_path": self.output_path,
            "error": self.error,
            "original_size_bytes": self.original_size_bytes,
            "quantized_size_bytes": self.quantized_size_bytes,
            "compression_ratio": self.compression_ratio,
            "quantization_type": self.quantization_type,
            "bits": self.bits,
        }


class ModelQuantizer:
    """
    Quantize models using various methods.
    
    Supports:
    - bitsandbytes (INT8, INT4)
    - GPTQ
    - AWQ
    """
    
    def __init__(self):
        """Initialize the quantizer."""
        self._check_dependencies()
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check available quantization libraries."""
        deps = {
            "bitsandbytes": False,
            "auto_gptq": False,
            "awq": False,
        }
        
        try:
            import bitsandbytes
            deps["bitsandbytes"] = True
        except ImportError:
            pass
        
        try:
            from auto_gptq import AutoGPTQForCausalLM
            deps["auto_gptq"] = True
        except ImportError:
            pass
        
        try:
            from awq import AutoAWQForCausalLM
            deps["awq"] = True
        except ImportError:
            pass
        
        return deps
    
    def quantize(
        self,
        model_path: str,
        output_path: str,
        config: QuantizationConfig,
        calibration_data: Optional[List[str]] = None,
    ) -> QuantizationResult:
        """
        Quantize a model.
        
        Args:
            model_path: Path to the source model
            output_path: Path for quantized model output
            config: Quantization configuration
            calibration_data: Optional calibration data for GPTQ/AWQ
        
        Returns:
            QuantizationResult
        """
        model_path = Path(model_path)
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Calculate original size
        original_size = self._get_model_size(model_path)
        
        try:
            if config.quant_type == QuantizationType.INT8:
                result = self._quantize_bitsandbytes(
                    model_path, output_path, bits=8
                )
            elif config.quant_type == QuantizationType.INT4:
                result = self._quantize_bitsandbytes(
                    model_path, output_path, bits=4
                )
            elif config.quant_type == QuantizationType.GPTQ:
                result = self._quantize_gptq(
                    model_path, output_path, config, calibration_data
                )
            elif config.quant_type == QuantizationType.AWQ:
                result = self._quantize_awq(
                    model_path, output_path, config, calibration_data
                )
            else:
                return QuantizationResult(
                    success=False,
                    output_path=str(output_path),
                    error=f"Unsupported quantization type: {config.quant_type}",
                )
            
            # Calculate compression ratio
            if result.success:
                quantized_size = self._get_model_size(output_path)
                result.original_size_bytes = original_size
                result.quantized_size_bytes = quantized_size
                result.compression_ratio = original_size / quantized_size if quantized_size > 0 else 0
            
            return result
            
        except Exception as e:
            logger.exception(f"Quantization failed: {e}")
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=str(e),
            )
    
    def _get_model_size(self, path: Path) -> int:
        """Get total model size in bytes."""
        if path.is_file():
            return path.stat().st_size
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    
    def _quantize_bitsandbytes(
        self,
        model_path: Path,
        output_path: Path,
        bits: int,
    ) -> QuantizationResult:
        """Quantize using bitsandbytes."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            
            # Create quantization config
            if bits == 8:
                bnb_config = BitsAndBytesConfig(load_in_8bit=True)
            else:  # 4-bit
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            
            # Load quantized model
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                quantization_config=bnb_config,
                device_map="auto",
            )
            
            # Save model
            model.save_pretrained(str(output_path))
            
            # Save tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            tokenizer.save_pretrained(str(output_path))
            
            return QuantizationResult(
                success=True,
                output_path=str(output_path),
                quantization_type=f"bitsandbytes-{bits}bit",
                bits=bits,
            )
            
        except ImportError as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=f"Missing dependency: {e}. Install with: pip install bitsandbytes",
            )
        except Exception as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=str(e),
            )
    
    def _quantize_gptq(
        self,
        model_path: Path,
        output_path: Path,
        config: QuantizationConfig,
        calibration_data: Optional[List[str]],
    ) -> QuantizationResult:
        """Quantize using GPTQ."""
        try:
            from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
            from transformers import AutoTokenizer
            
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            
            # Prepare calibration data
            if calibration_data:
                examples = [tokenizer(text, return_tensors="pt") for text in calibration_data[:128]]
            else:
                # Use default calibration data
                examples = [
                    tokenizer("Hello, how are you?", return_tensors="pt"),
                    tokenizer("The quick brown fox jumps over the lazy dog.", return_tensors="pt"),
                ]
            
            # Create quantization config
            quantize_config = BaseQuantizeConfig(
                bits=config.bits,
                group_size=config.group_size,
                desc_act=config.desc_act,
                sym=config.sym,
            )
            
            # Load and quantize
            model = AutoGPTQForCausalLM.from_pretrained(
                str(model_path),
                quantize_config=quantize_config,
            )
            
            model.quantize(examples)
            
            # Save
            model.save_quantized(str(output_path))
            tokenizer.save_pretrained(str(output_path))
            
            return QuantizationResult(
                success=True,
                output_path=str(output_path),
                quantization_type="gptq",
                bits=config.bits,
            )
            
        except ImportError as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=f"Missing dependency: {e}. Install with: pip install auto-gptq",
            )
        except Exception as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=str(e),
            )
    
    def _quantize_awq(
        self,
        model_path: Path,
        output_path: Path,
        config: QuantizationConfig,
        calibration_data: Optional[List[str]],
    ) -> QuantizationResult:
        """Quantize using AWQ."""
        try:
            from awq import AutoAWQForCausalLM
            from transformers import AutoTokenizer
            
            # Load model
            model = AutoAWQForCausalLM.from_pretrained(str(model_path))
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            
            # Quantization config
            quant_config = {
                "zero_point": True,
                "q_group_size": config.group_size,
                "w_bit": config.bits,
                "version": "GEMM",
            }
            
            # Quantize
            model.quantize(
                tokenizer,
                quant_config=quant_config,
                calib_data=calibration_data,
            )
            
            # Save
            model.save_quantized(str(output_path))
            tokenizer.save_pretrained(str(output_path))
            
            return QuantizationResult(
                success=True,
                output_path=str(output_path),
                quantization_type="awq",
                bits=config.bits,
            )
            
        except ImportError as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=f"Missing dependency: {e}. Install with: pip install autoawq",
            )
        except Exception as e:
            return QuantizationResult(
                success=False,
                output_path=str(output_path),
                error=str(e),
            )
    
    def get_supported_methods(self) -> List[str]:
        """Get list of available quantization methods."""
        deps = self._check_dependencies()
        methods = []
        
        if deps["bitsandbytes"]:
            methods.extend(["int8", "int4"])
        if deps["auto_gptq"]:
            methods.append("gptq")
        if deps["awq"]:
            methods.append("awq")
        
        return methods
