"""
Pre-built training configurations for nemotron-nano models.

Provides sensible defaults for SFT, LoRA, QLoRA, DPO, and full
fine-tuning on coding datasets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

NEMOTRON_BASE_MODEL = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"

NEMOTRON_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]


@dataclass
class NemotronSFTConfig:
    """SFT configuration optimized for nemotron-nano."""
    base_model: str = NEMOTRON_BASE_MODEL
    method: str = "sft"
    learning_rate: float = 2e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    max_seq_length: int = 4096
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    lr_scheduler: str = "cosine"
    bf16: bool = True
    gradient_checkpointing: bool = True
    packing: bool = True
    dataset_text_field: str = "text"
    report_to: str = "mlflow"
    output_dir: str = "./data/checkpoints/sft"


@dataclass
class NemotronLoRAConfig:
    """LoRA configuration optimized for nemotron-nano."""
    base_model: str = NEMOTRON_BASE_MODEL
    method: str = "lora"
    r: int = 64
    alpha: int = 128
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: list(NEMOTRON_TARGET_MODULES))
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    max_seq_length: int = 4096
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    lr_scheduler: str = "cosine"
    bf16: bool = True
    gradient_checkpointing: bool = True
    report_to: str = "mlflow"
    output_dir: str = "./data/checkpoints/lora"


@dataclass
class NemotronQLoRAConfig:
    """QLoRA configuration for memory-efficient nemotron training."""
    base_model: str = NEMOTRON_BASE_MODEL
    method: str = "qlora"
    bits: int = 4
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True
    r: int = 64
    alpha: int = 128
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: list(NEMOTRON_TARGET_MODULES))
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    max_seq_length: int = 4096
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    lr_scheduler: str = "cosine"
    bf16: bool = True
    gradient_checkpointing: bool = True
    report_to: str = "mlflow"
    output_dir: str = "./data/checkpoints/qlora"


@dataclass
class NemotronDPOConfig:
    """DPO configuration for preference alignment."""
    base_model: str = NEMOTRON_BASE_MODEL
    method: str = "dpo"
    beta: float = 0.1
    learning_rate: float = 5e-7
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    max_length: int = 2048
    max_prompt_length: int = 1024
    loss_type: str = "sigmoid"
    bf16: bool = True
    gradient_checkpointing: bool = True
    use_lora: bool = True
    lora_r: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    report_to: str = "mlflow"
    output_dir: str = "./data/checkpoints/dpo"


@dataclass
class NemotronFullConfig:
    """Full fine-tune configuration (requires significant GPU memory)."""
    base_model: str = NEMOTRON_BASE_MODEL
    method: str = "full"
    learning_rate: float = 1e-5
    num_epochs: int = 2
    batch_size: int = 1
    gradient_accumulation_steps: int = 16
    max_seq_length: int = 4096
    warmup_ratio: float = 0.05
    weight_decay: float = 0.01
    lr_scheduler: str = "cosine"
    bf16: bool = True
    gradient_checkpointing: bool = True
    report_to: str = "mlflow"
    output_dir: str = "./data/checkpoints/full"


_CONFIG_MAP = {
    "sft": NemotronSFTConfig,
    "lora": NemotronLoRAConfig,
    "qlora": NemotronQLoRAConfig,
    "dpo": NemotronDPOConfig,
    "full": NemotronFullConfig,
}


def get_training_config(
    method: str = "qlora",
    project_config: Optional[Dict[str, Any]] = None,
    **overrides,
) -> Any:
    """
    Build a training configuration for the given method.

    Merges project-level YAML settings with per-method defaults,
    then applies any explicit overrides.
    """
    config_cls = _CONFIG_MAP.get(method)
    if config_cls is None:
        raise ValueError(f"Unknown training method: {method}. Choose from: {list(_CONFIG_MAP)}")

    # Start from method defaults
    config = config_cls()

    # Apply project-level overrides from config.yaml
    if project_config:
        nemotron_cfg = project_config.get("nemotron", {})
        if nemotron_cfg.get("base_model"):
            config.base_model = nemotron_cfg["base_model"]

        training_cfg = project_config.get("training", {})
        method_cfg = training_cfg.get(method, {})
        for key, value in method_cfg.items():
            if hasattr(config, key):
                setattr(config, key, value)

    # Apply explicit overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config
