"""
TRL (Transformers Reinforcement Learning) adapter.

This adapter integrates with HuggingFace's TRL library for RLHF and DPO training.

Reference: https://github.com/huggingface/trl
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.rl.adapters.base import BaseRLAdapter, RLTrainingResult
from agentic_assistants.rl.config import RLConfig, RLMethod, DPOConfig, PPOConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class TRLAdapter(BaseRLAdapter):
    """
    Adapter for TRL (Transformers Reinforcement Learning).
    
    Supports:
    - DPO (Direct Preference Optimization)
    - PPO with reward models
    - Reward model training
    - ORPO and KTO (newer methods)
    """
    
    def __init__(self):
        """Initialize the TRL adapter."""
        self._version = self._detect_version()
    
    @property
    def name(self) -> str:
        return "trl"
    
    @property
    def supported_methods(self) -> List[RLMethod]:
        return [
            RLMethod.DPO,
            RLMethod.PPO,
            RLMethod.REWARD_MODEL,
            RLMethod.RLHF,
            RLMethod.ORPO,
            RLMethod.KTO,
        ]
    
    def _detect_version(self) -> str:
        """Detect TRL version."""
        try:
            import trl
            return trl.__version__
        except ImportError:
            return "not_installed"
        except Exception:
            return "unknown"
    
    def is_available(self) -> bool:
        """Check if TRL is available."""
        try:
            import trl
            return True
        except ImportError:
            return False
    
    async def train_dpo(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using Direct Preference Optimization.
        
        DPO directly optimizes the policy to prefer chosen over rejected responses
        without needing an explicit reward model.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="TRL not installed. Install with: pip install trl",
            )
        
        errors = self.validate_config(config)
        if errors:
            return RLTrainingResult(
                success=False,
                error=f"Configuration errors: {', '.join(errors)}",
            )
        
        start_time = time.time()
        
        try:
            # Import TRL components
            from trl import DPOTrainer, DPOConfig as TRLDPOConfig
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from datasets import load_dataset
            
            import torch
            
            dpo_config = config.dpo_config or DPOConfig()
            output_dir = config.output_dir or f"./data/rl/outputs/dpo-{int(time.time())}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting DPO training for {config.base_model}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                config.base_model,
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
                device_map="auto",
            )
            
            # Reference model (can be None for DPO to copy from model)
            ref_model = None
            if dpo_config.ref_model:
                ref_model = AutoModelForCausalLM.from_pretrained(
                    dpo_config.ref_model,
                    torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
                    device_map="auto",
                )
            
            # Load dataset
            # For now, we'll load from a JSON file based on dataset_id
            dataset_path = f"./data/training/datasets/{config.preference_dataset_id}.json"
            if Path(dataset_path).exists():
                train_dataset = load_dataset("json", data_files=dataset_path, split="train")
            else:
                # Try loading from HuggingFace
                train_dataset = load_dataset(config.preference_dataset_id, split="train")
            
            # Apply LoRA if configured
            if dpo_config.use_lora:
                try:
                    from peft import LoraConfig, get_peft_model
                    peft_config = LoraConfig(
                        r=dpo_config.lora_r,
                        lora_alpha=dpo_config.lora_alpha,
                        lora_dropout=dpo_config.lora_dropout,
                        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                        task_type="CAUSAL_LM",
                    )
                    model = get_peft_model(model, peft_config)
                except ImportError:
                    logger.warning("PEFT not available, training without LoRA")
            
            # Configure DPO training
            training_args = TRLDPOConfig(
                output_dir=output_dir,
                beta=dpo_config.beta,
                loss_type=dpo_config.loss_type,
                learning_rate=dpo_config.learning_rate,
                per_device_train_batch_size=dpo_config.batch_size,
                gradient_accumulation_steps=dpo_config.gradient_accumulation_steps,
                num_train_epochs=dpo_config.num_train_epochs,
                lr_scheduler_type=dpo_config.lr_scheduler_type,
                warmup_ratio=dpo_config.warmup_ratio,
                max_grad_norm=dpo_config.max_grad_norm,
                bf16=config.bf16,
                gradient_checkpointing=config.gradient_checkpointing,
                logging_steps=10,
                save_steps=100,
                max_length=dpo_config.max_length,
                max_prompt_length=dpo_config.max_prompt_length,
                report_to=config.report_to,
            )
            
            # Create trainer
            trainer = DPOTrainer(
                model=model,
                ref_model=ref_model,
                args=training_args,
                train_dataset=train_dataset,
                tokenizer=tokenizer,
            )
            
            # Train
            logger.info("Starting DPO training...")
            train_result = trainer.train()
            
            # Save model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            # Get final metrics
            metrics = {
                "train_loss": train_result.training_loss,
                "train_runtime": train_result.metrics.get("train_runtime", 0),
                "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
            }
            
            if metrics_callback:
                metrics_callback(metrics)
            
            return RLTrainingResult(
                success=True,
                model_path=output_dir,
                method=RLMethod.DPO,
                metrics=metrics,
                total_steps=train_result.global_step,
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            logger.exception(f"DPO training failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.DPO,
                training_time_seconds=time.time() - start_time,
            )
    
    async def train_ppo(
        self,
        config: RLConfig,
        reward_model_path: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using PPO with a reward model.
        
        This is the classic RLHF approach where:
        1. A reward model scores generated responses
        2. PPO optimizes the policy to maximize reward
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="TRL not installed. Install with: pip install trl",
            )
        
        start_time = time.time()
        
        try:
            from trl import PPOTrainer, PPOConfig as TRLPPOConfig, AutoModelForCausalLMWithValueHead
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            from datasets import load_dataset
            import torch
            
            ppo_config = config.ppo_config or PPOConfig()
            output_dir = config.output_dir or f"./data/rl/outputs/ppo-{int(time.time())}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting PPO training for {config.base_model}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load policy model with value head
            model = AutoModelForCausalLMWithValueHead.from_pretrained(
                config.base_model,
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
            )
            
            # Load reward model
            reward_model = AutoModelForSequenceClassification.from_pretrained(
                reward_model_path,
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
            )
            reward_tokenizer = AutoTokenizer.from_pretrained(reward_model_path)
            
            # Load prompts dataset
            if config.prompt_dataset_id:
                dataset_path = f"./data/training/datasets/{config.prompt_dataset_id}.json"
                if Path(dataset_path).exists():
                    dataset = load_dataset("json", data_files=dataset_path, split="train")
                else:
                    dataset = load_dataset(config.prompt_dataset_id, split="train")
            else:
                # Use preference dataset prompts
                dataset_path = f"./data/training/datasets/{config.preference_dataset_id}.json"
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            
            # Configure PPO
            training_args = TRLPPOConfig(
                output_dir=output_dir,
                learning_rate=ppo_config.learning_rate,
                batch_size=ppo_config.batch_size,
                mini_batch_size=ppo_config.mini_batch_size,
                gradient_accumulation_steps=ppo_config.gradient_accumulation_steps,
                ppo_epochs=ppo_config.ppo_epochs,
                gamma=ppo_config.gamma,
                lam=ppo_config.lam,
                cliprange=ppo_config.cliprange,
                cliprange_value=ppo_config.cliprange_value,
                vf_coef=ppo_config.vf_coef,
                init_kl_coef=ppo_config.init_kl_coef,
                target_kl=ppo_config.target_kl,
                adap_kl_ctrl=ppo_config.adap_kl_ctrl,
            )
            
            # Create trainer
            trainer = PPOTrainer(
                config=training_args,
                model=model,
                tokenizer=tokenizer,
                dataset=dataset,
            )
            
            # Training loop
            logger.info("Starting PPO training loop...")
            
            generation_kwargs = {
                "max_new_tokens": ppo_config.max_new_tokens,
                "top_k": ppo_config.top_k,
                "top_p": ppo_config.top_p,
                "temperature": ppo_config.temperature,
                "do_sample": True,
            }
            
            total_steps = 0
            total_reward = 0.0
            
            for epoch in range(3):  # Default 3 epochs
                for batch in trainer.dataloader:
                    query_tensors = batch["input_ids"]
                    
                    # Generate responses
                    response_tensors = trainer.generate(
                        query_tensors,
                        return_prompt=False,
                        **generation_kwargs,
                    )
                    
                    # Compute rewards
                    texts = tokenizer.batch_decode(
                        torch.cat([query_tensors, response_tensors], dim=-1),
                        skip_special_tokens=True,
                    )
                    
                    # Get rewards from reward model
                    reward_inputs = reward_tokenizer(
                        texts, return_tensors="pt", padding=True, truncation=True
                    )
                    with torch.no_grad():
                        rewards = reward_model(**reward_inputs).logits.squeeze()
                    
                    # PPO step
                    stats = trainer.step(query_tensors, response_tensors, rewards)
                    
                    total_steps += 1
                    total_reward += rewards.mean().item()
                    
                    if metrics_callback:
                        metrics_callback({
                            "step": total_steps,
                            "mean_reward": rewards.mean().item(),
                            "kl": stats.get("objective/kl", 0),
                        })
            
            # Save model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            return RLTrainingResult(
                success=True,
                model_path=output_dir,
                method=RLMethod.PPO,
                metrics={
                    "mean_reward": total_reward / max(total_steps, 1),
                    "total_steps": total_steps,
                },
                total_steps=total_steps,
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            logger.exception(f"PPO training failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.PPO,
                training_time_seconds=time.time() - start_time,
            )
    
    async def train_reward_model(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train a reward model on preference data.
        
        The reward model learns to predict human preferences and is used
        in PPO training to provide reward signals.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="TRL not installed. Install with: pip install trl",
            )
        
        start_time = time.time()
        
        try:
            from trl import RewardTrainer, RewardConfig as TRLRewardConfig
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            from datasets import load_dataset
            import torch
            
            reward_config = config.reward_config
            output_dir = config.output_dir or f"./data/rl/outputs/reward-{int(time.time())}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting reward model training from {config.base_model}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model for sequence classification (reward prediction)
            model = AutoModelForSequenceClassification.from_pretrained(
                config.base_model,
                num_labels=1,  # Single reward value
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
            )
            
            # Load preference dataset
            dataset_path = f"./data/training/datasets/{config.preference_dataset_id}.json"
            if Path(dataset_path).exists():
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            else:
                dataset = load_dataset(config.preference_dataset_id, split="train")
            
            # Configure reward training
            training_args = TRLRewardConfig(
                output_dir=output_dir,
                learning_rate=reward_config.learning_rate if reward_config else 1e-5,
                per_device_train_batch_size=reward_config.batch_size if reward_config else 8,
                num_train_epochs=reward_config.num_epochs if reward_config else 1,
                bf16=config.bf16,
                logging_steps=10,
                save_steps=100,
            )
            
            # Create trainer
            trainer = RewardTrainer(
                model=model,
                args=training_args,
                tokenizer=tokenizer,
                train_dataset=dataset,
            )
            
            # Train
            logger.info("Starting reward model training...")
            train_result = trainer.train()
            
            # Save model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            # Evaluate accuracy
            # Simple accuracy: check if reward(chosen) > reward(rejected)
            accuracy = self._evaluate_reward_model(model, tokenizer, dataset)
            
            return RLTrainingResult(
                success=True,
                model_path=output_dir,
                method=RLMethod.REWARD_MODEL,
                metrics={
                    "train_loss": train_result.training_loss,
                    "accuracy": accuracy,
                },
                reward_model_path=output_dir,
                reward_model_accuracy=accuracy,
                total_steps=train_result.global_step,
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            logger.exception(f"Reward model training failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.REWARD_MODEL,
                training_time_seconds=time.time() - start_time,
            )
    
    def _evaluate_reward_model(
        self,
        model,
        tokenizer,
        dataset,
        num_samples: int = 100,
    ) -> float:
        """Evaluate reward model accuracy on preference data."""
        import torch
        
        correct = 0
        total = 0
        
        model.eval()
        with torch.no_grad():
            for i, sample in enumerate(dataset):
                if i >= num_samples:
                    break
                
                prompt = sample.get("prompt", "")
                chosen = sample.get("chosen", "")
                rejected = sample.get("rejected", "")
                
                # Get rewards
                chosen_text = f"{prompt} {chosen}"
                rejected_text = f"{prompt} {rejected}"
                
                chosen_inputs = tokenizer(chosen_text, return_tensors="pt", truncation=True)
                rejected_inputs = tokenizer(rejected_text, return_tensors="pt", truncation=True)
                
                chosen_reward = model(**chosen_inputs).logits.item()
                rejected_reward = model(**rejected_inputs).logits.item()
                
                if chosen_reward > rejected_reward:
                    correct += 1
                total += 1
        
        return correct / total if total > 0 else 0.0
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get TRL adapter capabilities."""
        return {
            "name": "TRL (Transformers Reinforcement Learning)",
            "version": self._version,
            "available": self.is_available(),
            "supported_methods": [m.value for m in self.supported_methods],
            "features": {
                "dpo": True,
                "ppo": True,
                "reward_modeling": True,
                "orpo": True,
                "kto": True,
                "distributed_training": True,
                "lora_support": True,
            },
        }
