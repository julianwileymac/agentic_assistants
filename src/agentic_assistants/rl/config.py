"""
Configuration for reinforcement learning training.

This module defines configuration classes for various RL methods
including RLHF, DPO, PPO, and reward modeling.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RLMethod(str, Enum):
    """Reinforcement learning methods."""
    RLHF = "rlhf"           # Full RLHF with reward model
    DPO = "dpo"             # Direct Preference Optimization
    PPO = "ppo"             # Proximal Policy Optimization
    REWARD_MODEL = "rm"     # Reward model training
    ORPO = "orpo"           # Odds Ratio Preference Optimization
    KTO = "kto"             # Kahneman-Tversky Optimization
    SFT = "sft"             # Supervised Fine-Tuning (pre-RL step)


class RewardConfig(BaseModel):
    """Configuration for reward model."""
    
    model_name_or_path: Optional[str] = Field(None, description="Reward model path or ID")
    
    # Architecture
    hidden_size: int = Field(default=768, description="Hidden size")
    num_hidden_layers: int = Field(default=6, description="Number of layers")
    
    # Training
    learning_rate: float = Field(default=1e-5, description="Learning rate")
    batch_size: int = Field(default=8, description="Batch size")
    num_epochs: int = Field(default=1, description="Number of epochs")
    
    # Regularization
    dropout: float = Field(default=0.1, description="Dropout rate")
    weight_decay: float = Field(default=0.01, description="Weight decay")
    
    class Config:
        extra = "allow"


class PPOConfig(BaseModel):
    """Configuration for PPO training."""
    
    # PPO hyperparameters
    learning_rate: float = Field(default=1.41e-5, description="Learning rate")
    batch_size: int = Field(default=128, description="Batch size")
    mini_batch_size: int = Field(default=1, description="Mini batch size")
    gradient_accumulation_steps: int = Field(default=1, description="Gradient accumulation")
    
    # PPO-specific
    ppo_epochs: int = Field(default=4, description="PPO epochs per update")
    gamma: float = Field(default=1.0, description="Discount factor")
    lam: float = Field(default=0.95, description="GAE lambda")
    cliprange: float = Field(default=0.2, description="PPO clip range")
    cliprange_value: float = Field(default=0.2, description="Value function clip range")
    vf_coef: float = Field(default=0.1, description="Value function coefficient")
    
    # KL penalty
    init_kl_coef: float = Field(default=0.2, description="Initial KL coefficient")
    target_kl: float = Field(default=6.0, description="Target KL divergence")
    kl_penalty: str = Field(default="kl", description="KL penalty type: kl, abs, mse")
    
    # Generation
    max_new_tokens: int = Field(default=128, description="Max new tokens")
    top_k: int = Field(default=0, description="Top-k sampling")
    top_p: float = Field(default=1.0, description="Top-p (nucleus) sampling")
    temperature: float = Field(default=1.0, description="Temperature")
    
    # Optimization
    adap_kl_ctrl: bool = Field(default=True, description="Adaptive KL control")
    
    class Config:
        extra = "allow"


class DPOConfig(BaseModel):
    """Configuration for DPO training."""
    
    # DPO hyperparameters
    beta: float = Field(default=0.1, description="DPO beta parameter")
    loss_type: str = Field(default="sigmoid", description="Loss type: sigmoid, hinge, ipo")
    label_smoothing: float = Field(default=0.0, description="Label smoothing")
    
    # Training
    learning_rate: float = Field(default=5e-7, description="Learning rate")
    batch_size: int = Field(default=4, description="Batch size")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation")
    num_train_epochs: int = Field(default=1, description="Number of epochs")
    
    # Reference model
    ref_model: Optional[str] = Field(None, description="Reference model (None = copy of base)")
    precompute_ref_log_probs: bool = Field(default=False, description="Precompute reference log probs")
    
    # Optimization
    lr_scheduler_type: str = Field(default="cosine", description="LR scheduler")
    warmup_ratio: float = Field(default=0.1, description="Warmup ratio")
    max_grad_norm: float = Field(default=1.0, description="Max gradient norm")
    
    # Generation for evaluation
    max_length: int = Field(default=512, description="Max sequence length")
    max_prompt_length: int = Field(default=256, description="Max prompt length")
    
    # LoRA (optional)
    use_lora: bool = Field(default=True, description="Use LoRA for training")
    lora_r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")
    
    class Config:
        extra = "allow"


class ORPOConfig(BaseModel):
    """Configuration for ORPO (Odds Ratio Preference Optimization) training."""

    # ORPO hyperparameters
    beta: float = Field(default=0.1, description="ORPO beta parameter (odds ratio weight)")
    learning_rate: float = Field(default=8e-6, description="Learning rate")
    batch_size: int = Field(default=4, description="Batch size")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation")
    num_train_epochs: int = Field(default=1, description="Number of epochs")

    # Optimization
    lr_scheduler_type: str = Field(default="cosine", description="LR scheduler")
    warmup_ratio: float = Field(default=0.1, description="Warmup ratio")
    max_grad_norm: float = Field(default=1.0, description="Max gradient norm")

    # Sequence lengths
    max_length: int = Field(default=1024, description="Max sequence length")
    max_prompt_length: int = Field(default=512, description="Max prompt length")

    # LoRA (optional)
    use_lora: bool = Field(default=True, description="Use LoRA for training")
    lora_r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")

    class Config:
        extra = "allow"


class KTOConfig(BaseModel):
    """Configuration for KTO (Kahneman-Tversky Optimization) training."""

    # KTO hyperparameters
    beta: float = Field(default=0.1, description="KTO beta parameter")
    desirable_weight: float = Field(default=1.0, description="Weight for desirable examples")
    undesirable_weight: float = Field(default=1.0, description="Weight for undesirable examples")

    # Training
    learning_rate: float = Field(default=5e-7, description="Learning rate")
    batch_size: int = Field(default=4, description="Batch size")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation")
    num_train_epochs: int = Field(default=1, description="Number of epochs")

    # Optimization
    lr_scheduler_type: str = Field(default="cosine", description="LR scheduler")
    warmup_ratio: float = Field(default=0.1, description="Warmup ratio")
    max_grad_norm: float = Field(default=1.0, description="Max gradient norm")

    # Sequence lengths
    max_length: int = Field(default=1024, description="Max sequence length")
    max_prompt_length: int = Field(default=512, description="Max prompt length")

    # LoRA (optional)
    use_lora: bool = Field(default=True, description="Use LoRA for training")
    lora_r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")

    class Config:
        extra = "allow"


class SFTConfig(BaseModel):
    """Configuration for Supervised Fine-Tuning (pre-RL step)."""

    # Training
    learning_rate: float = Field(default=2e-5, description="Learning rate")
    batch_size: int = Field(default=4, description="Batch size")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation")
    num_train_epochs: int = Field(default=3, description="Number of epochs")

    # Optimization
    lr_scheduler_type: str = Field(default="cosine", description="LR scheduler")
    warmup_ratio: float = Field(default=0.03, description="Warmup ratio")
    weight_decay: float = Field(default=0.001, description="Weight decay")
    max_grad_norm: float = Field(default=1.0, description="Max gradient norm")

    # Sequence lengths
    max_seq_length: int = Field(default=2048, description="Max sequence length")
    packing: bool = Field(default=False, description="Pack multiple samples into one sequence")

    # Dataset format
    dataset_text_field: str = Field(default="text", description="Field name for text in dataset")

    # LoRA (optional)
    use_lora: bool = Field(default=True, description="Use LoRA for training")
    lora_r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")

    class Config:
        extra = "allow"


class RLHFConfig(BaseModel):
    """Configuration for full RLHF pipeline."""
    
    # Component configs
    reward_config: RewardConfig = Field(default_factory=RewardConfig)
    ppo_config: PPOConfig = Field(default_factory=PPOConfig)
    
    # Pipeline settings
    reward_model_path: Optional[str] = Field(None, description="Pre-trained reward model")
    train_reward_model: bool = Field(default=True, description="Train reward model")
    
    # SFT (optional initial fine-tuning)
    sft_model_path: Optional[str] = Field(None, description="SFT model path")
    run_sft: bool = Field(default=False, description="Run SFT before RLHF")
    
    # Human feedback settings
    feedback_batch_size: int = Field(default=100, description="Samples per feedback batch")
    feedback_iterations: int = Field(default=5, description="Feedback collection iterations")
    
    class Config:
        extra = "allow"


class RLConfig(BaseModel):
    """
    Main RL configuration.
    
    This is the top-level configuration for RL training that can be used
    for any RL method (RLHF, DPO, PPO, etc.).
    """
    
    # Method selection
    method: RLMethod = Field(default=RLMethod.DPO, description="RL method to use")
    
    # Model settings
    base_model: str = Field(..., description="Base model path or HuggingFace ID")
    output_name: str = Field(..., description="Name for the trained model")
    output_dir: Optional[str] = Field(None, description="Output directory")
    
    # Dataset
    preference_dataset_id: str = Field(..., description="Preference dataset ID")
    prompt_dataset_id: Optional[str] = Field(None, description="Prompt dataset for generation")
    
    # Method-specific configs
    dpo_config: Optional[DPOConfig] = Field(None, description="DPO configuration")
    ppo_config: Optional[PPOConfig] = Field(None, description="PPO configuration")
    rlhf_config: Optional[RLHFConfig] = Field(None, description="Full RLHF configuration")
    reward_config: Optional[RewardConfig] = Field(None, description="Reward model configuration")
    orpo_config: Optional[ORPOConfig] = Field(None, description="ORPO configuration")
    kto_config: Optional[KTOConfig] = Field(None, description="KTO configuration")
    sft_config: Optional[SFTConfig] = Field(None, description="SFT configuration")
    
    # Common training settings
    bf16: bool = Field(default=True, description="Use BF16")
    gradient_checkpointing: bool = Field(default=True, description="Gradient checkpointing")
    
    # Logging
    report_to: List[str] = Field(default_factory=lambda: ["mlflow"], description="Logging backends")
    mlflow_experiment_name: Optional[str] = Field(None, description="MLFlow experiment")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags")
    description: Optional[str] = Field(None, description="Description")
    
    class Config:
        extra = "allow"
    
    def get_method_config(self) -> BaseModel:
        """Get the configuration for the selected method."""
        if self.method == RLMethod.DPO:
            return self.dpo_config or DPOConfig()
        elif self.method == RLMethod.PPO:
            return self.ppo_config or PPOConfig()
        elif self.method == RLMethod.RLHF:
            return self.rlhf_config or RLHFConfig()
        elif self.method == RLMethod.REWARD_MODEL:
            return self.reward_config or RewardConfig()
        elif self.method == RLMethod.ORPO:
            return self.orpo_config or ORPOConfig()
        elif self.method == RLMethod.KTO:
            return self.kto_config or KTOConfig()
        elif self.method == RLMethod.SFT:
            return self.sft_config or SFTConfig()
        else:
            return DPOConfig()


@dataclass
class PreferenceData:
    """A single preference data point."""
    
    prompt: str
    chosen: str
    rejected: str
    
    # Optional metadata
    chosen_score: Optional[float] = None
    rejected_score: Optional[float] = None
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "chosen": self.chosen,
            "rejected": self.rejected,
            "chosen_score": self.chosen_score,
            "rejected_score": self.rejected_score,
            "source": self.source,
        }


@dataclass
class HumanFeedback:
    """Human feedback for RLHF."""
    
    id: str
    prompt: str
    response_a: str
    response_b: str
    
    # Preference: 1 = A preferred, 2 = B preferred, 0 = tie
    preference: int = 0
    
    # Optional ratings
    rating_a: Optional[float] = None
    rating_b: Optional[float] = None
    
    # Feedback metadata
    annotator_id: Optional[str] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None
    
    def to_preference_data(self) -> Optional[PreferenceData]:
        """Convert to PreferenceData based on preference."""
        if self.preference == 1:
            return PreferenceData(
                prompt=self.prompt,
                chosen=self.response_a,
                rejected=self.response_b,
                chosen_score=self.rating_a,
                rejected_score=self.rating_b,
            )
        elif self.preference == 2:
            return PreferenceData(
                prompt=self.prompt,
                chosen=self.response_b,
                rejected=self.response_a,
                chosen_score=self.rating_b,
                rejected_score=self.rating_a,
            )
        return None
