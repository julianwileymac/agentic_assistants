# Chunk: de84fdd4c7a7_1

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 90-165
- chunk: 2/8

```
turn False
    
    def validate_config(self, config: TrainingConfig) -> List[str]:
        """Validate training configuration."""
        errors = []
        
        if not config.base_model:
            errors.append("base_model is required")
        
        if not config.output_name:
            errors.append("output_name is required")
        
        if not config.dataset_id:
            errors.append("dataset_id is required")
        
        if config.method == TrainingMethod.QLORA:
            if not config.qlora_config:
                # Will use defaults, which is fine
                pass
        
        if config.learning_rate <= 0:
            errors.append("learning_rate must be positive")
        
        if config.num_epochs < 1:
            errors.append("num_epochs must be at least 1")
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get framework capabilities."""
        return {
            "name": "Llama Factory",
            "training_methods": ["full", "lora", "qlora", "adapter"],
            "supports_rlhf": True,
            "supports_dpo": True,
            "supports_quantization": True,
            "quantization_types": ["4bit", "8bit"],
            "supports_distributed": True,
            "supports_deepspeed": True,
            "supported_model_types": [
                "llama", "llama2", "llama3", "mistral", "mixtral",
                "qwen", "qwen2", "yi", "chatglm", "baichuan",
                "phi", "gemma", "deepseek"
            ],
            "dataset_formats": ["alpaca", "sharegpt", "openai"],
        }
    
    def estimate_resources(self, config: TrainingConfig) -> Dict[str, Any]:
        """Estimate resource requirements."""
        # Basic estimation based on model size and method
        base_memory_gb = 8  # Default estimate
        
        # Adjust based on training method
        if config.method == TrainingMethod.FULL:
            memory_multiplier = 4.0  # Full fine-tuning needs more memory
        elif config.method == TrainingMethod.LORA:
            memory_multiplier = 1.5
        elif config.method == TrainingMethod.QLORA:
            memory_multiplier = 1.0  # QLoRA is most memory efficient
        else:
            memory_multiplier = 2.0
        
        # Adjust for batch size
        batch_multiplier = config.batch_size / 4.0
        
        estimated_memory_gb = base_memory_gb * memory_multiplier * batch_multiplier
        
        # Estimate time (very rough)
        estimated_hours = config.num_epochs * 0.5  # Very rough estimate
        
        return {
            "estimated_gpu_memory_gb": estimated_memory_gb,
            "estimated_training_hours": estimated_hours,
            "recommended_gpu": "RTX 3090/4090 or A100" if estimated_memory_gb > 16 else "RTX 3080 or better",
            "supports_cpu_training": config.method == TrainingMethod.QLORA,
```
