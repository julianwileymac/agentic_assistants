# Chunk: 42d9bcef09ee_1

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 96-161
- chunk: 2/8

```
     
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
```
