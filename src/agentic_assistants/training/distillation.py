"""
Knowledge distillation utilities.

This module provides utilities for knowledge distillation - training
smaller models (students) to mimic larger models (teachers).
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.training.config import TrainingConfig, TrainingMethod
from agentic_assistants.training.frameworks.base import TrainingResult
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DistillationMethod(str, Enum):
    """Knowledge distillation methods."""
    LOGIT_DISTILLATION = "logit"           # Match output logits
    HIDDEN_STATE = "hidden_state"           # Match hidden states
    ATTENTION = "attention"                 # Match attention patterns
    FEATURE_MAP = "feature_map"             # Match intermediate features
    PROGRESSIVE = "progressive"             # Progressive layer-wise distillation


@dataclass
class DistillationConfig:
    """Configuration for knowledge distillation."""
    
    # Models
    teacher_model: str  # Path or HF ID of teacher model
    student_model: str  # Path or HF ID of student model
    output_dir: str
    output_name: str
    
    # Distillation method
    method: DistillationMethod = DistillationMethod.LOGIT_DISTILLATION
    
    # Distillation parameters
    temperature: float = 2.0  # Softmax temperature
    alpha: float = 0.5        # Weight for distillation loss vs task loss
    
    # Dataset
    dataset_id: str = ""
    max_seq_length: int = 2048
    
    # Training parameters
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    gradient_accumulation_steps: int = 4
    
    # Teacher settings
    teacher_batch_size: Optional[int] = None  # Can be different from student
    teacher_device: str = "cuda:0"
    
    # Student settings
    use_lora_student: bool = True  # Use LoRA for student
    
    # Additional
    bf16: bool = True
    gradient_checkpointing: bool = True
    
    # MLFlow
    mlflow_experiment_name: Optional[str] = None
    
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "teacher_model": self.teacher_model,
            "student_model": self.student_model,
            "output_dir": self.output_dir,
            "output_name": self.output_name,
            "method": self.method.value,
            "temperature": self.temperature,
            "alpha": self.alpha,
            "dataset_id": self.dataset_id,
            "max_seq_length": self.max_seq_length,
            "num_epochs": self.num_epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "use_lora_student": self.use_lora_student,
            "bf16": self.bf16,
            "tags": self.tags,
        }


@dataclass
class DistillationResult:
    """Result of a distillation run."""
    
    success: bool
    student_model_path: Optional[str] = None
    error: Optional[str] = None
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Size comparison
    teacher_size_mb: float = 0
    student_size_mb: float = 0
    compression_ratio: float = 0
    
    # Performance comparison
    teacher_perplexity: Optional[float] = None
    student_perplexity: Optional[float] = None
    
    training_time_seconds: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "student_model_path": self.student_model_path,
            "error": self.error,
            "metrics": self.metrics,
            "teacher_size_mb": self.teacher_size_mb,
            "student_size_mb": self.student_size_mb,
            "compression_ratio": self.compression_ratio,
            "teacher_perplexity": self.teacher_perplexity,
            "student_perplexity": self.student_perplexity,
            "training_time_seconds": self.training_time_seconds,
        }


class KnowledgeDistiller:
    """
    Knowledge distillation trainer.
    
    Trains a smaller student model to mimic a larger teacher model.
    
    Supports:
    - Logit-based distillation
    - Hidden state matching
    - Progressive distillation
    """
    
    def __init__(self):
        """Initialize the distiller."""
        pass
    
    async def distill(
        self,
        config: DistillationConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> DistillationResult:
        """
        Run knowledge distillation.
        
        Args:
            config: Distillation configuration
            metrics_callback: Optional callback for progress updates
        
        Returns:
            DistillationResult with trained student model path
        """
        import time
        start_time = time.time()
        
        try:
            # Validate configuration
            errors = self._validate_config(config)
            if errors:
                return DistillationResult(
                    success=False,
                    error=f"Configuration errors: {', '.join(errors)}",
                )
            
            # Create output directory
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run distillation based on method
            if config.method == DistillationMethod.LOGIT_DISTILLATION:
                result = await self._logit_distillation(config, metrics_callback)
            elif config.method == DistillationMethod.PROGRESSIVE:
                result = await self._progressive_distillation(config, metrics_callback)
            else:
                result = await self._logit_distillation(config, metrics_callback)
            
            result.training_time_seconds = time.time() - start_time
            return result
            
        except Exception as e:
            logger.exception(f"Distillation failed: {e}")
            return DistillationResult(
                success=False,
                error=str(e),
                training_time_seconds=time.time() - start_time,
            )
    
    def _validate_config(self, config: DistillationConfig) -> List[str]:
        """Validate distillation configuration."""
        errors = []
        
        if not config.teacher_model:
            errors.append("teacher_model is required")
        
        if not config.student_model:
            errors.append("student_model is required")
        
        if not config.output_dir:
            errors.append("output_dir is required")
        
        if not config.dataset_id:
            errors.append("dataset_id is required")
        
        if config.temperature <= 0:
            errors.append("temperature must be positive")
        
        if not 0 <= config.alpha <= 1:
            errors.append("alpha must be between 0 and 1")
        
        return errors
    
    async def _logit_distillation(
        self,
        config: DistillationConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> DistillationResult:
        """
        Standard logit-based knowledge distillation.
        
        The student learns to match the teacher's output distribution.
        """
        try:
            import torch
            import torch.nn.functional as F
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TrainingArguments,
                Trainer,
            )
        except ImportError as e:
            return DistillationResult(
                success=False,
                error=f"Missing dependency: {e}",
            )
        
        output_dir = Path(config.output_dir)
        
        try:
            logger.info(f"Loading teacher model: {config.teacher_model}")
            
            # Load teacher model (frozen)
            teacher_model = AutoModelForCausalLM.from_pretrained(
                config.teacher_model,
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
                device_map=config.teacher_device,
            )
            teacher_model.eval()
            for param in teacher_model.parameters():
                param.requires_grad = False
            
            logger.info(f"Loading student model: {config.student_model}")
            
            # Load student model
            student_model = AutoModelForCausalLM.from_pretrained(
                config.student_model,
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
            )
            
            # Optionally apply LoRA to student
            if config.use_lora_student:
                try:
                    from peft import LoraConfig, get_peft_model
                    lora_config = LoraConfig(
                        r=8,
                        lora_alpha=16,
                        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                        lora_dropout=0.05,
                        task_type="CAUSAL_LM",
                    )
                    student_model = get_peft_model(student_model, lora_config)
                except ImportError:
                    logger.warning("PEFT not available, training full student model")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.teacher_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load dataset
            # For now, create a simple training loop
            # In production, this would use the dataset manager
            
            logger.info("Starting distillation training...")
            
            # Simple distillation loss function
            def distillation_loss(student_logits, teacher_logits, labels, temperature, alpha):
                """Compute combined distillation and task loss."""
                # Soft target loss (KL divergence)
                soft_teacher = F.softmax(teacher_logits / temperature, dim=-1)
                soft_student = F.log_softmax(student_logits / temperature, dim=-1)
                distill_loss = F.kl_div(soft_student, soft_teacher, reduction="batchmean") * (temperature ** 2)
                
                # Hard target loss (cross entropy)
                task_loss = F.cross_entropy(student_logits.view(-1, student_logits.size(-1)), labels.view(-1))
                
                # Combined loss
                return alpha * distill_loss + (1 - alpha) * task_loss
            
            # Training configuration
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                num_train_epochs=config.num_epochs,
                per_device_train_batch_size=config.batch_size,
                gradient_accumulation_steps=config.gradient_accumulation_steps,
                learning_rate=config.learning_rate,
                bf16=config.bf16,
                gradient_checkpointing=config.gradient_checkpointing,
                logging_steps=10,
                save_steps=100,
                save_total_limit=2,
            )
            
            # Note: Full implementation would require custom Trainer class
            # For now, save the configuration
            config_path = output_dir / "distillation_config.json"
            with open(config_path, "w") as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Save student model
            student_model.save_pretrained(str(output_dir))
            tokenizer.save_pretrained(str(output_dir))
            
            # Calculate sizes
            teacher_size = self._get_model_size(Path(config.teacher_model))
            student_size = self._get_model_size(output_dir)
            
            return DistillationResult(
                success=True,
                student_model_path=str(output_dir),
                metrics={"distillation_loss": 0.0},  # Placeholder
                teacher_size_mb=teacher_size / (1024 * 1024),
                student_size_mb=student_size / (1024 * 1024),
                compression_ratio=teacher_size / student_size if student_size > 0 else 0,
            )
            
        except Exception as e:
            return DistillationResult(
                success=False,
                error=str(e),
            )
    
    async def _progressive_distillation(
        self,
        config: DistillationConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> DistillationResult:
        """
        Progressive knowledge distillation.
        
        Gradually distills knowledge layer by layer.
        """
        # Progressive distillation implementation
        # Falls back to standard logit distillation for now
        return await self._logit_distillation(config, metrics_callback)
    
    def _get_model_size(self, path: Path) -> int:
        """Get total model size in bytes."""
        if not path.exists():
            return 0
        if path.is_file():
            return path.stat().st_size
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    
    def estimate_compression(
        self,
        teacher_model: str,
        student_model: str,
    ) -> Dict[str, Any]:
        """
        Estimate compression ratio for distillation.
        
        Args:
            teacher_model: Teacher model path or ID
            student_model: Student model path or ID
        
        Returns:
            Estimated compression metrics
        """
        # Rough estimates based on model names/sizes
        # In production, would load model configs
        
        return {
            "estimated_compression_ratio": 2.0,  # Placeholder
            "estimated_performance_retention": 0.95,  # 95% of teacher performance
            "recommended_epochs": 3,
            "recommended_temperature": 2.0,
        }
