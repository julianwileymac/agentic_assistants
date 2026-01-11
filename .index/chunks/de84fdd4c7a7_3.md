# Chunk: de84fdd4c7a7_3

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 219-299
- chunk: 4/8

```
nfig["template"] = self._get_template_for_model(config.base_model)
        lf_config["cutoff_len"] = config.max_seq_length
        
        # Training hyperparameters
        lf_config["num_train_epochs"] = config.num_epochs
        lf_config["per_device_train_batch_size"] = config.batch_size
        lf_config["gradient_accumulation_steps"] = config.gradient_accumulation_steps
        lf_config["learning_rate"] = config.learning_rate
        lf_config["lr_scheduler_type"] = config.lr_scheduler_type
        lf_config["warmup_ratio"] = config.warmup_ratio
        lf_config["max_grad_norm"] = config.max_grad_norm
        
        # Optimization
        lf_config["optim"] = config.optim
        lf_config["fp16"] = config.fp16
        lf_config["bf16"] = config.bf16
        
        # Checkpointing
        lf_config["save_steps"] = config.save_steps
        lf_config["save_total_limit"] = config.save_total_limit
        lf_config["logging_steps"] = config.logging_steps
        
        # MLFlow integration
        if "mlflow" in config.report_to:
            lf_config["report_to"] = "mlflow"
            if config.mlflow_experiment_name:
                lf_config["mlflow_experiment_name"] = config.mlflow_experiment_name
            if config.mlflow_run_name:
                lf_config["run_name"] = config.mlflow_run_name
        
        # Add any framework-specific config
        lf_config.update(config.framework_config)
        
        return lf_config
    
    def _get_template_for_model(self, model_name: str) -> str:
        """Get the chat template for a model."""
        model_lower = model_name.lower()
        
        if "llama-3" in model_lower or "llama3" in model_lower:
            return "llama3"
        elif "llama-2" in model_lower or "llama2" in model_lower:
            return "llama2"
        elif "mistral" in model_lower:
            return "mistral"
        elif "qwen2" in model_lower:
            return "qwen2"
        elif "qwen" in model_lower:
            return "qwen"
        elif "phi" in model_lower:
            return "phi"
        elif "gemma" in model_lower:
            return "gemma"
        elif "yi" in model_lower:
            return "yi"
        elif "deepseek" in model_lower:
            return "deepseek"
        else:
            return "default"
    
    async def train(
        self,
        config: TrainingConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TrainingResult:
        """
        Run training with Llama Factory.
        
        Args:
            config: Training configuration
            metrics_callback: Callback for metrics updates
        
        Returns:
            TrainingResult with model path and metrics
        """
        # Validate config
        errors = self.validate_config(config)
        if errors:
            return TrainingResult(
                success=False,
```
