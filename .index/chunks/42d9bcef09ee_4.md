# Chunk: 42d9bcef09ee_4

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 282-352
- chunk: 5/8

```
      dataset_path = f"./data/training/datasets/{config.preference_dataset_id}.json"
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            
            # Configure PPO
            training_args = TRLPPOConfig(
                output_dir=output_dir,
                learning_rate=ppo_config.learning_rate,
                batch_size=ppo_config.batch_size,
                mini_batch_size=ppo_config.mini_batch_size,
                gradient_accumulation_steps=ppo_config.gradient_accumulation_steps,
                ppo_epochs=ppo_config.ppo_epochs,
                gamma=ppo_config.gamma,
                lam=ppo_config.lam,
                cliprange=ppo_config.cliprange,
                cliprange_value=ppo_config.cliprange_value,
                vf_coef=ppo_config.vf_coef,
                init_kl_coef=ppo_config.init_kl_coef,
                target_kl=ppo_config.target_kl,
                adap_kl_ctrl=ppo_config.adap_kl_ctrl,
            )
            
            # Create trainer
            trainer = PPOTrainer(
                config=training_args,
                model=model,
                tokenizer=tokenizer,
                dataset=dataset,
            )
            
            # Training loop
            logger.info("Starting PPO training loop...")
            
            generation_kwargs = {
                "max_new_tokens": ppo_config.max_new_tokens,
                "top_k": ppo_config.top_k,
                "top_p": ppo_config.top_p,
                "temperature": ppo_config.temperature,
                "do_sample": True,
            }
            
            total_steps = 0
            total_reward = 0.0
            
            for epoch in range(3):  # Default 3 epochs
                for batch in trainer.dataloader:
                    query_tensors = batch["input_ids"]
                    
                    # Generate responses
                    response_tensors = trainer.generate(
                        query_tensors,
                        return_prompt=False,
                        **generation_kwargs,
                    )
                    
                    # Compute rewards
                    texts = tokenizer.batch_decode(
                        torch.cat([query_tensors, response_tensors], dim=-1),
                        skip_special_tokens=True,
                    )
                    
                    # Get rewards from reward model
                    reward_inputs = reward_tokenizer(
                        texts, return_tensors="pt", padding=True, truncation=True
                    )
                    with torch.no_grad():
                        rewards = reward_model(**reward_inputs).logits.squeeze()
                    
                    # PPO step
                    stats = trainer.step(query_tensors, response_tensors, rewards)
                    
```
