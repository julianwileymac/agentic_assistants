"""
Training configuration models.

This module defines Pydantic models for training configurations including
LoRA, QLoRA, full fine-tuning, and quantization settings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TrainingMethod(str, Enum):
    """Training method types."""
    FULL = "full"
    LORA = "lora"
    QLORA = "qlora"
    ADAPTER = "adapter"


class QuantizationType(str, Enum):
    """Quantization types for model compression."""
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    GPTQ = "gptq"
    AWQ = "awq"
    GGUF = "gguf"


class LoRAConfig(BaseModel):
    """Configuration for LoRA (Low-Rank Adaptation) training."""
    
    r: int = Field(default=8, description="LoRA attention dimension (rank)")
    lora_alpha: int = Field(default=16, description="LoRA alpha parameter for scaling")
    lora_dropout: float = Field(default=0.05, description="Dropout probability for LoRA layers")
    target_modules: List[str] = Field(
        default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        description="Target modules for LoRA adaptation"
    )
    bias: str = Field(default="none", description="Bias type: none, all, or lora_only")
    task_type: str = Field(default="CAUSAL_LM", description="Task type for PEFT")
    
    class Config:
        extra = "allow"


class QLoRAConfig(LoRAConfig):
    """Configuration for QLoRA (Quantized LoRA) training."""
    
    load_in_4bit: bool = Field(default=True, description="Load model in 4-bit precision")
    bnb_4bit_compute_dtype: str = Field(default="bfloat16", description="Compute dtype for 4-bit")
    bnb_4bit_quant_type: str = Field(default="nf4", description="Quantization type: fp4 or nf4")
    bnb_4bit_use_double_quant: bool = Field(default=True, description="Use nested quantization")


class FullFinetuneConfig(BaseModel):
    """Configuration for full model fine-tuning."""
    
    freeze_embeddings: bool = Field(default=False, description="Freeze embedding layers")
    freeze_layers: Optional[List[int]] = Field(default=None, description="Specific layers to freeze")
    gradient_checkpointing: bool = Field(default=True, description="Use gradient checkpointing")
    
    class Config:
        extra = "allow"


class QuantizationConfig(BaseModel):
    """Configuration for model quantization."""
    
    quant_type: QuantizationType = Field(default=QuantizationType.NONE)
    bits: int = Field(default=4, description="Number of bits for quantization")
    group_size: int = Field(default=128, description="Group size for quantization")
    desc_act: bool = Field(default=True, description="Descending activation order")
    sym: bool = Field(default=False, description="Symmetric quantization")
    
    # GGUF-specific settings
    gguf_model_type: Optional[str] = Field(default=None, description="GGUF model type")
    
    class Config:
        extra = "allow"


class TrainingConfig(BaseModel):
    """
    Main training configuration.
    
    This configuration defines all parameters needed for a training job
    including the base model, training method, hyperparameters, and output settings.
    """
    
    # Model settings
    base_model: str = Field(..., description="Base model name or path (HuggingFace ID or local path)")
    model_revision: Optional[str] = Field(default=None, description="Model revision/branch")
    output_name: str = Field(..., description="Name for the trained model")
    output_dir: Optional[str] = Field(default=None, description="Output directory (auto-generated if None)")
    
    # Training method
    method: TrainingMethod = Field(default=TrainingMethod.LORA, description="Training method")
    lora_config: Optional[LoRAConfig] = Field(default=None, description="LoRA configuration")
    qlora_config: Optional[QLoRAConfig] = Field(default=None, description="QLoRA configuration")
    full_config: Optional[FullFinetuneConfig] = Field(default=None, description="Full fine-tune config")
    
    # Dataset settings
    dataset_id: str = Field(..., description="Dataset ID from training dataset registry")
    dataset_format: str = Field(default="alpaca", description="Dataset format: alpaca, sharegpt, custom")
    max_seq_length: int = Field(default=2048, description="Maximum sequence length")
    
    # Training hyperparameters
    num_epochs: int = Field(default=3, description="Number of training epochs")
    batch_size: int = Field(default=4, description="Training batch size")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation steps")
    learning_rate: float = Field(default=2e-4, description="Learning rate")
    lr_scheduler_type: str = Field(default="cosine", description="Learning rate scheduler")
    warmup_ratio: float = Field(default=0.03, description="Warmup ratio")
    weight_decay: float = Field(default=0.001, description="Weight decay")
    max_grad_norm: float = Field(default=1.0, description="Max gradient norm for clipping")
    
    # Optimization settings
    optim: str = Field(default="adamw_torch", description="Optimizer type")
    fp16: bool = Field(default=False, description="Use FP16 training")
    bf16: bool = Field(default=True, description="Use BF16 training")
    gradient_checkpointing: bool = Field(default=True, description="Use gradient checkpointing")
    
    # Evaluation settings
    eval_strategy: str = Field(default="steps", description="Evaluation strategy")
    eval_steps: int = Field(default=100, description="Evaluation frequency in steps")
    save_strategy: str = Field(default="steps", description="Checkpoint save strategy")
    save_steps: int = Field(default=100, description="Checkpoint save frequency")
    save_total_limit: int = Field(default=3, description="Maximum checkpoints to keep")
    
    # Logging
    logging_steps: int = Field(default=10, description="Logging frequency")
    report_to: List[str] = Field(default_factory=lambda: ["mlflow"], description="Logging integrations")
    
    # Resource settings
    num_gpus: int = Field(default=1, description="Number of GPUs to use")
    per_device_train_batch_size: Optional[int] = Field(default=None, description="Per-device batch size")
    
    # Quantization for output
    quantization: Optional[QuantizationConfig] = Field(default=None, description="Output quantization")
    
    # MLFlow settings
    mlflow_experiment_name: Optional[str] = Field(default=None, description="MLFlow experiment name")
    mlflow_run_name: Optional[str] = Field(default=None, description="MLFlow run name")
    
    # Framework-specific settings
    framework: str = Field(default="llama_factory", description="Training framework to use")
    framework_config: Dict[str, Any] = Field(default_factory=dict, description="Framework-specific config")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for the training job")
    description: Optional[str] = Field(default=None, description="Training job description")
    
    class Config:
        extra = "allow"
    
    def get_effective_lora_config(self) -> Optional[Union[LoRAConfig, QLoRAConfig]]:
        """Get the effective LoRA configuration based on training method."""
        if self.method == TrainingMethod.QLORA:
            return self.qlora_config or QLoRAConfig()
        elif self.method == TrainingMethod.LORA:
            return self.lora_config or LoRAConfig()
        return None
    
    def to_training_args(self) -> Dict[str, Any]:
        """Convert to HuggingFace TrainingArguments-compatible dict."""
        return {
            "output_dir": self.output_dir,
            "num_train_epochs": self.num_epochs,
            "per_device_train_batch_size": self.per_device_train_batch_size or self.batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "learning_rate": self.learning_rate,
            "lr_scheduler_type": self.lr_scheduler_type,
            "warmup_ratio": self.warmup_ratio,
            "weight_decay": self.weight_decay,
            "max_grad_norm": self.max_grad_norm,
            "optim": self.optim,
            "fp16": self.fp16,
            "bf16": self.bf16,
            "gradient_checkpointing": self.gradient_checkpointing,
            "evaluation_strategy": self.eval_strategy,
            "eval_steps": self.eval_steps,
            "save_strategy": self.save_strategy,
            "save_steps": self.save_steps,
            "save_total_limit": self.save_total_limit,
            "logging_steps": self.logging_steps,
            "report_to": self.report_to,
        }


@dataclass
class CustomModelInfo:
    """Information about a custom trained model."""
    
    id: str
    name: str
    base_model: str
    training_method: TrainingMethod
    training_job_id: str
    
    # Paths
    local_path: str
    hf_repo_id: Optional[str] = None
    
    # Status
    status: str = "created"  # created, deployed, archived
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Configuration used
    training_config: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    # MLFlow tracking
    mlflow_run_id: Optional[str] = None
    mlflow_model_uri: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "base_model": self.base_model,
            "training_method": self.training_method.value if isinstance(self.training_method, TrainingMethod) else self.training_method,
            "training_job_id": self.training_job_id,
            "local_path": self.local_path,
            "hf_repo_id": self.hf_repo_id,
            "status": self.status,
            "metrics": self.metrics,
            "training_config": self.training_config,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "description": self.description,
            "mlflow_run_id": self.mlflow_run_id,
            "mlflow_model_uri": self.mlflow_model_uri,
        }
