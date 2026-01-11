"""
Llama Factory training framework adapter.

This module provides integration with Llama Factory for LLM training.
Llama Factory supports efficient fine-tuning with LoRA, QLoRA, and full fine-tuning.

Reference: https://github.com/hiyouga/LLaMA-Factory
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.training.config import (
    TrainingConfig,
    TrainingMethod,
    LoRAConfig,
    QLoRAConfig,
)
from agentic_assistants.training.frameworks.base import BaseTrainingFramework, TrainingResult
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class LlamaFactoryAdapter(BaseTrainingFramework):
    """
    Adapter for Llama Factory training framework.
    
    Llama Factory provides efficient fine-tuning for LLMs with support for:
    - Full fine-tuning
    - LoRA (Low-Rank Adaptation)
    - QLoRA (Quantized LoRA)
    - RLHF/DPO training
    
    This adapter translates our TrainingConfig into Llama Factory's configuration
    format and manages the training process.
    """
    
    def __init__(self, llama_factory_path: Optional[str] = None):
        """
        Initialize the Llama Factory adapter.
        
        Args:
            llama_factory_path: Path to Llama Factory installation
        """
        self._llama_factory_path = llama_factory_path
        self._version = self._detect_version()
    
    @property
    def name(self) -> str:
        return "llama_factory"
    
    @property
    def version(self) -> str:
        return self._version
    
    def _detect_version(self) -> str:
        """Detect Llama Factory version."""
        try:
            # Try to import and get version
            result = subprocess.run(
                [sys.executable, "-c", "import llamafactory; print(llamafactory.__version__)"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def is_available(self) -> bool:
        """Check if Llama Factory is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import llamafactory"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def validate_config(self, config: TrainingConfig) -> List[str]:
        """Validate training configuration."""
        errors = []
        
        if not config.base_model:
            errors.append("base_model is required")
        
        if not config.output_name:
            errors.append("output_name is required")
        
        if not config.dataset_id:
            errors.append("dataset_id is required")
        
        if config.method == TrainingMethod.QLORA:
            if not config.qlora_config:
                # Will use defaults, which is fine
                pass
        
        if config.learning_rate <= 0:
            errors.append("learning_rate must be positive")
        
        if config.num_epochs < 1:
            errors.append("num_epochs must be at least 1")
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get framework capabilities."""
        return {
            "name": "Llama Factory",
            "training_methods": ["full", "lora", "qlora", "adapter"],
            "supports_rlhf": True,
            "supports_dpo": True,
            "supports_quantization": True,
            "quantization_types": ["4bit", "8bit"],
            "supports_distributed": True,
            "supports_deepspeed": True,
            "supported_model_types": [
                "llama", "llama2", "llama3", "mistral", "mixtral",
                "qwen", "qwen2", "yi", "chatglm", "baichuan",
                "phi", "gemma", "deepseek"
            ],
            "dataset_formats": ["alpaca", "sharegpt", "openai"],
        }
    
    def estimate_resources(self, config: TrainingConfig) -> Dict[str, Any]:
        """Estimate resource requirements."""
        # Basic estimation based on model size and method
        base_memory_gb = 8  # Default estimate
        
        # Adjust based on training method
        if config.method == TrainingMethod.FULL:
            memory_multiplier = 4.0  # Full fine-tuning needs more memory
        elif config.method == TrainingMethod.LORA:
            memory_multiplier = 1.5
        elif config.method == TrainingMethod.QLORA:
            memory_multiplier = 1.0  # QLoRA is most memory efficient
        else:
            memory_multiplier = 2.0
        
        # Adjust for batch size
        batch_multiplier = config.batch_size / 4.0
        
        estimated_memory_gb = base_memory_gb * memory_multiplier * batch_multiplier
        
        # Estimate time (very rough)
        estimated_hours = config.num_epochs * 0.5  # Very rough estimate
        
        return {
            "estimated_gpu_memory_gb": estimated_memory_gb,
            "estimated_training_hours": estimated_hours,
            "recommended_gpu": "RTX 3090/4090 or A100" if estimated_memory_gb > 16 else "RTX 3080 or better",
            "supports_cpu_training": config.method == TrainingMethod.QLORA,
        }
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default Llama Factory configuration."""
        return {
            "stage": "sft",
            "do_train": True,
            "finetuning_type": "lora",
            "lora_target": "q_proj,v_proj,k_proj,o_proj,gate_proj,up_proj,down_proj",
            "lora_rank": 8,
            "lora_alpha": 16,
            "lora_dropout": 0.05,
            "cutoff_len": 2048,
            "max_samples": 100000,
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 4,
            "lr_scheduler_type": "cosine",
            "logging_steps": 10,
            "save_steps": 100,
            "warmup_ratio": 0.03,
            "optim": "adamw_torch",
            "fp16": False,
            "bf16": True,
        }
    
    def _build_config(self, config: TrainingConfig) -> Dict[str, Any]:
        """Build Llama Factory configuration from TrainingConfig."""
        lf_config = self.get_default_config()
        
        # Model settings
        lf_config["model_name_or_path"] = config.base_model
        lf_config["output_dir"] = config.output_dir
        
        # Training method
        if config.method == TrainingMethod.FULL:
            lf_config["finetuning_type"] = "full"
        elif config.method == TrainingMethod.LORA:
            lf_config["finetuning_type"] = "lora"
            if config.lora_config:
                lf_config["lora_rank"] = config.lora_config.r
                lf_config["lora_alpha"] = config.lora_config.lora_alpha
                lf_config["lora_dropout"] = config.lora_config.lora_dropout
                lf_config["lora_target"] = ",".join(config.lora_config.target_modules)
        elif config.method == TrainingMethod.QLORA:
            lf_config["finetuning_type"] = "lora"
            lf_config["quantization_bit"] = 4
            if config.qlora_config:
                lf_config["lora_rank"] = config.qlora_config.r
                lf_config["lora_alpha"] = config.qlora_config.lora_alpha
                lf_config["lora_dropout"] = config.qlora_config.lora_dropout
                lf_config["lora_target"] = ",".join(config.qlora_config.target_modules)
        
        # Dataset
        lf_config["dataset"] = config.dataset_id
        lf_config["template"] = self._get_template_for_model(config.base_model)
        lf_config["cutoff_len"] = config.max_seq_length
        
        # Training hyperparameters
        lf_config["num_train_epochs"] = config.num_epochs
        lf_config["per_device_train_batch_size"] = config.batch_size
        lf_config["gradient_accumulation_steps"] = config.gradient_accumulation_steps
        lf_config["learning_rate"] = config.learning_rate
        lf_config["lr_scheduler_type"] = config.lr_scheduler_type
        lf_config["warmup_ratio"] = config.warmup_ratio
        lf_config["max_grad_norm"] = config.max_grad_norm
        
        # Optimization
        lf_config["optim"] = config.optim
        lf_config["fp16"] = config.fp16
        lf_config["bf16"] = config.bf16
        
        # Checkpointing
        lf_config["save_steps"] = config.save_steps
        lf_config["save_total_limit"] = config.save_total_limit
        lf_config["logging_steps"] = config.logging_steps
        
        # MLFlow integration
        if "mlflow" in config.report_to:
            lf_config["report_to"] = "mlflow"
            if config.mlflow_experiment_name:
                lf_config["mlflow_experiment_name"] = config.mlflow_experiment_name
            if config.mlflow_run_name:
                lf_config["run_name"] = config.mlflow_run_name
        
        # Add any framework-specific config
        lf_config.update(config.framework_config)
        
        return lf_config
    
    def _get_template_for_model(self, model_name: str) -> str:
        """Get the chat template for a model."""
        model_lower = model_name.lower()
        
        if "llama-3" in model_lower or "llama3" in model_lower:
            return "llama3"
        elif "llama-2" in model_lower or "llama2" in model_lower:
            return "llama2"
        elif "mistral" in model_lower:
            return "mistral"
        elif "qwen2" in model_lower:
            return "qwen2"
        elif "qwen" in model_lower:
            return "qwen"
        elif "phi" in model_lower:
            return "phi"
        elif "gemma" in model_lower:
            return "gemma"
        elif "yi" in model_lower:
            return "yi"
        elif "deepseek" in model_lower:
            return "deepseek"
        else:
            return "default"
    
    async def train(
        self,
        config: TrainingConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TrainingResult:
        """
        Run training with Llama Factory.
        
        Args:
            config: Training configuration
            metrics_callback: Callback for metrics updates
        
        Returns:
            TrainingResult with model path and metrics
        """
        # Validate config
        errors = self.validate_config(config)
        if errors:
            return TrainingResult(
                success=False,
                error=f"Configuration errors: {', '.join(errors)}",
            )
        
        # Check availability
        if not self.is_available():
            return TrainingResult(
                success=False,
                error="Llama Factory is not installed. Install with: pip install llamafactory",
            )
        
        # Build Llama Factory config
        lf_config = self._build_config(config)
        
        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write config to file
        config_file = output_dir / "training_config.json"
        with open(config_file, "w") as f:
            json.dump(lf_config, f, indent=2)
        
        logger.info(f"Starting Llama Factory training with config: {config_file}")
        
        start_time = time.time()
        
        try:
            # Run training
            result = await self._run_training_process(
                config_file=str(config_file),
                output_dir=str(output_dir),
                metrics_callback=metrics_callback,
            )
            
            training_time = time.time() - start_time
            
            if result["success"]:
                return TrainingResult(
                    success=True,
                    model_path=str(output_dir),
                    metrics=result.get("metrics", {}),
                    total_steps=result.get("total_steps", 0),
                    total_epochs=config.num_epochs,
                    training_time_seconds=training_time,
                )
            else:
                return TrainingResult(
                    success=False,
                    error=result.get("error", "Unknown error"),
                    training_time_seconds=training_time,
                )
                
        except Exception as e:
            logger.exception(f"Training failed: {e}")
            return TrainingResult(
                success=False,
                error=str(e),
                training_time_seconds=time.time() - start_time,
            )
    
    async def _run_training_process(
        self,
        config_file: str,
        output_dir: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Run the training process."""
        
        # Build command
        cmd = [
            sys.executable, "-m", "llamafactory.cli", "train",
            config_file,
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=self._llama_factory_path,
        )
        
        metrics = {}
        total_steps = 0
        
        # Stream output and parse metrics
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_str = line.decode("utf-8", errors="ignore").strip()
            logger.debug(line_str)
            
            # Parse metrics from output
            parsed = self._parse_training_output(line_str)
            if parsed:
                metrics.update(parsed)
                total_steps = parsed.get("step", total_steps)
                
                if metrics_callback:
                    metrics_callback(parsed)
        
        await process.wait()
        
        if process.returncode == 0:
            return {
                "success": True,
                "metrics": metrics,
                "total_steps": total_steps,
            }
        else:
            return {
                "success": False,
                "error": f"Training process exited with code {process.returncode}",
            }
    
    def _parse_training_output(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse training output line for metrics."""
        metrics = {}
        
        # Look for loss values
        if "loss" in line.lower():
            try:
                # Try to parse JSON-style output
                if "{" in line and "}" in line:
                    json_str = line[line.index("{"):line.rindex("}")+1]
                    data = json.loads(json_str)
                    return data
                
                # Parse "loss: X.XXX" style
                import re
                loss_match = re.search(r"loss[:\s]+([0-9.]+)", line, re.IGNORECASE)
                if loss_match:
                    metrics["loss"] = float(loss_match.group(1))
                
                # Parse step information
                step_match = re.search(r"step[:\s]+(\d+)", line, re.IGNORECASE)
                if step_match:
                    metrics["step"] = int(step_match.group(1))
                
                # Parse learning rate
                lr_match = re.search(r"lr[:\s]+([0-9.e-]+)", line, re.IGNORECASE)
                if lr_match:
                    metrics["learning_rate"] = float(lr_match.group(1))
                
                # Parse epoch
                epoch_match = re.search(r"epoch[:\s]+([0-9.]+)", line, re.IGNORECASE)
                if epoch_match:
                    metrics["epoch"] = float(epoch_match.group(1))
                    
            except Exception:
                pass
        
        return metrics if metrics else None
    
    async def train_dpo(
        self,
        config: TrainingConfig,
        preference_dataset_id: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TrainingResult:
        """
        Run DPO (Direct Preference Optimization) training.
        
        Args:
            config: Training configuration
            preference_dataset_id: ID of preference dataset
            metrics_callback: Callback for metrics updates
        
        Returns:
            TrainingResult
        """
        # Modify config for DPO
        lf_config = self._build_config(config)
        lf_config["stage"] = "dpo"
        lf_config["dataset"] = preference_dataset_id
        lf_config["dpo_beta"] = config.framework_config.get("dpo_beta", 0.1)
        lf_config["dpo_loss"] = config.framework_config.get("dpo_loss", "sigmoid")
        
        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write config
        config_file = output_dir / "dpo_config.json"
        with open(config_file, "w") as f:
            json.dump(lf_config, f, indent=2)
        
        start_time = time.time()
        
        try:
            result = await self._run_training_process(
                config_file=str(config_file),
                output_dir=str(output_dir),
                metrics_callback=metrics_callback,
            )
            
            return TrainingResult(
                success=result["success"],
                model_path=str(output_dir) if result["success"] else None,
                error=result.get("error"),
                metrics=result.get("metrics", {}),
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            return TrainingResult(
                success=False,
                error=str(e),
                training_time_seconds=time.time() - start_time,
            )
    
    async def train_reward_model(
        self,
        config: TrainingConfig,
        preference_dataset_id: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TrainingResult:
        """
        Train a reward model for RLHF.
        
        Args:
            config: Training configuration
            preference_dataset_id: ID of preference dataset
            metrics_callback: Callback for metrics updates
        
        Returns:
            TrainingResult
        """
        # Modify config for reward model training
        lf_config = self._build_config(config)
        lf_config["stage"] = "rm"  # Reward modeling
        lf_config["dataset"] = preference_dataset_id
        
        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write config
        config_file = output_dir / "rm_config.json"
        with open(config_file, "w") as f:
            json.dump(lf_config, f, indent=2)
        
        start_time = time.time()
        
        try:
            result = await self._run_training_process(
                config_file=str(config_file),
                output_dir=str(output_dir),
                metrics_callback=metrics_callback,
            )
            
            return TrainingResult(
                success=result["success"],
                model_path=str(output_dir) if result["success"] else None,
                error=result.get("error"),
                metrics=result.get("metrics", {}),
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            return TrainingResult(
                success=False,
                error=str(e),
                training_time_seconds=time.time() - start_time,
            )
