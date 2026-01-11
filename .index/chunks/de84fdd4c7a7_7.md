# Chunk: de84fdd4c7a7_7

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 513-567
- chunk: 8/8

```
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
```
