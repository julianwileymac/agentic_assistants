# Chunk: 42d9bcef09ee_2

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 154-230
- chunk: 3/8

```
                logger.warning("PEFT not available, training without LoRA")
            
            # Configure DPO training
            training_args = TRLDPOConfig(
                output_dir=output_dir,
                beta=dpo_config.beta,
                loss_type=dpo_config.loss_type,
                learning_rate=dpo_config.learning_rate,
                per_device_train_batch_size=dpo_config.batch_size,
                gradient_accumulation_steps=dpo_config.gradient_accumulation_steps,
                num_train_epochs=dpo_config.num_train_epochs,
                lr_scheduler_type=dpo_config.lr_scheduler_type,
                warmup_ratio=dpo_config.warmup_ratio,
                max_grad_norm=dpo_config.max_grad_norm,
                bf16=config.bf16,
                gradient_checkpointing=config.gradient_checkpointing,
                logging_steps=10,
                save_steps=100,
                max_length=dpo_config.max_length,
                max_prompt_length=dpo_config.max_prompt_length,
                report_to=config.report_to,
            )
            
            # Create trainer
            trainer = DPOTrainer(
                model=model,
                ref_model=ref_model,
                args=training_args,
                train_dataset=train_dataset,
                tokenizer=tokenizer,
            )
            
            # Train
            logger.info("Starting DPO training...")
            train_result = trainer.train()
            
            # Save model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            # Get final metrics
            metrics = {
                "train_loss": train_result.training_loss,
                "train_runtime": train_result.metrics.get("train_runtime", 0),
                "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
            }
            
            if metrics_callback:
                metrics_callback(metrics)
            
            return RLTrainingResult(
                success=True,
                model_path=output_dir,
                method=RLMethod.DPO,
                metrics=metrics,
                total_steps=train_result.global_step,
                training_time_seconds=time.time() - start_time,
            )
            
        except Exception as e:
            logger.exception(f"DPO training failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.DPO,
                training_time_seconds=time.time() - start_time,
            )
    
    async def train_ppo(
        self,
        config: RLConfig,
        reward_model_path: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using PPO with a reward model.
```
