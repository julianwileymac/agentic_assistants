# Chunk: 42d9bcef09ee_5

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 345-420
- chunk: 6/8

```
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
```
