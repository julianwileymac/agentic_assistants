# Chunk: de84fdd4c7a7_4

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 289-375
- chunk: 5/8

```
_callback: Callback for metrics updates
        
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
        
```
