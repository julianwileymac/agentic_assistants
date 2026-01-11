# Chunk: 42d9bcef09ee_6

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 413-483
- chunk: 7/8

```
t(time.time())}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Starting reward model training from {config.base_model}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.base_model)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model for sequence classification (reward prediction)
            model = AutoModelForSequenceClassification.from_pretrained(
                config.base_model,
                num_labels=1,  # Single reward value
                torch_dtype=torch.bfloat16 if config.bf16 else torch.float32,
            )
            
            # Load preference dataset
            dataset_path = f"./data/training/datasets/{config.preference_dataset_id}.json"
            if Path(dataset_path).exists():
                dataset = load_dataset("json", data_files=dataset_path, split="train")
            else:
                dataset = load_dataset(config.preference_dataset_id, split="train")
            
            # Configure reward training
            training_args = TRLRewardConfig(
                output_dir=output_dir,
                learning_rate=reward_config.learning_rate if reward_config else 1e-5,
                per_device_train_batch_size=reward_config.batch_size if reward_config else 8,
                num_train_epochs=reward_config.num_epochs if reward_config else 1,
                bf16=config.bf16,
                logging_steps=10,
                save_steps=100,
            )
            
            # Create trainer
            trainer = RewardTrainer(
                model=model,
                args=training_args,
                tokenizer=tokenizer,
                train_dataset=dataset,
            )
            
            # Train
            logger.info("Starting reward model training...")
            train_result = trainer.train()
            
            # Save model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            # Evaluate accuracy
            # Simple accuracy: check if reward(chosen) > reward(rejected)
            accuracy = self._evaluate_reward_model(model, tokenizer, dataset)
            
            return RLTrainingResult(
                success=True,
                model_path=output_dir,
                method=RLMethod.REWARD_MODEL,
                metrics={
                    "train_loss": train_result.training_loss,
                    "accuracy": accuracy,
                },
                reward_model_path=output_dir,
                reward_model_accuracy=accuracy,
                total_steps=train_result.global_step,
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
```
