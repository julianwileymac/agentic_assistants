# Chunk: 42d9bcef09ee_3

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 219-288
- chunk: 4/8

```
start_time,
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
```
