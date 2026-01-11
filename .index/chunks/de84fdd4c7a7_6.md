# Chunk: de84fdd4c7a7_6

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 439-523
- chunk: 7/8

```
up(1))
                
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
```
