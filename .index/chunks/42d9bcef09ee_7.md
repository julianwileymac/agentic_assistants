# Chunk: 42d9bcef09ee_7

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 474-547
- chunk: 8/8

```
,
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
```
