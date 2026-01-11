# Chunk: de84fdd4c7a7_2

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 161-225
- chunk: 3/8

```
     "estimated_gpu_memory_gb": estimated_memory_gb,
            "estimated_training_hours": estimated_hours,
            "recommended_gpu": "RTX 3090/4090 or A100" if estimated_memory_gb > 16 else "RTX 3080 or better",
            "supports_cpu_training": config.method == TrainingMethod.QLORA,
        }
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default Llama Factory configuration."""
        return {
            "stage": "sft",
            "do_train": True,
            "finetuning_type": "lora",
            "lora_target": "q_proj,v_proj,k_proj,o_proj,gate_proj,up_proj,down_proj",
            "lora_rank": 8,
            "lora_alpha": 16,
            "lora_dropout": 0.05,
            "cutoff_len": 2048,
            "max_samples": 100000,
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 4,
            "lr_scheduler_type": "cosine",
            "logging_steps": 10,
            "save_steps": 100,
            "warmup_ratio": 0.03,
            "optim": "adamw_torch",
            "fp16": False,
            "bf16": True,
        }
    
    def _build_config(self, config: TrainingConfig) -> Dict[str, Any]:
        """Build Llama Factory configuration from TrainingConfig."""
        lf_config = self.get_default_config()
        
        # Model settings
        lf_config["model_name_or_path"] = config.base_model
        lf_config["output_dir"] = config.output_dir
        
        # Training method
        if config.method == TrainingMethod.FULL:
            lf_config["finetuning_type"] = "full"
        elif config.method == TrainingMethod.LORA:
            lf_config["finetuning_type"] = "lora"
            if config.lora_config:
                lf_config["lora_rank"] = config.lora_config.r
                lf_config["lora_alpha"] = config.lora_config.lora_alpha
                lf_config["lora_dropout"] = config.lora_config.lora_dropout
                lf_config["lora_target"] = ",".join(config.lora_config.target_modules)
        elif config.method == TrainingMethod.QLORA:
            lf_config["finetuning_type"] = "lora"
            lf_config["quantization_bit"] = 4
            if config.qlora_config:
                lf_config["lora_rank"] = config.qlora_config.r
                lf_config["lora_alpha"] = config.qlora_config.lora_alpha
                lf_config["lora_dropout"] = config.qlora_config.lora_dropout
                lf_config["lora_target"] = ",".join(config.qlora_config.target_modules)
        
        # Dataset
        lf_config["dataset"] = config.dataset_id
        lf_config["template"] = self._get_template_for_model(config.base_model)
        lf_config["cutoff_len"] = config.max_seq_length
        
        # Training hyperparameters
        lf_config["num_train_epochs"] = config.num_epochs
        lf_config["per_device_train_batch_size"] = config.batch_size
```
