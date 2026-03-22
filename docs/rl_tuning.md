# RL/RLHF Tuning Guide

This guide covers reinforcement learning methods for aligning LLMs with human preferences.

## Overview

The RL subsystem supports multiple alignment methods:
- **DPO (Direct Preference Optimization)**: Simple, no reward model needed
- **PPO (Proximal Policy Optimization)**: Fine-grained control with reward model
- **RLHF (Reinforcement Learning from Human Feedback)**: Full pipeline with feedback collection
- **ORPO (Odds Ratio Preference Optimization)**: Memory-efficient alternative to DPO
- **KTO (Kahneman-Tversky Optimization)**: Works with binary feedback

## When to Use RL Methods

| Method | Best For | Requirements |
|--------|----------|--------------|
| DPO | Quick alignment, limited compute | Preference pairs |
| PPO | Maximum control, production | Reward model, preference pairs |
| RLHF | Interactive feedback loops | Human annotators |
| ORPO | Memory-constrained environments | Preference pairs |
| KTO | Binary feedback only | Thumbs up/down data |

## Quick Start with DPO

DPO is the recommended starting point - it's simpler than PPO and doesn't require training a separate reward model.

### 1. Prepare Preference Data

Preference data consists of prompts with chosen (better) and rejected (worse) responses:

```json
[
  {
    "prompt": "What is machine learning?",
    "chosen": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
    "rejected": "Machine learning is when computers learn stuff."
  }
]
```

### 2. Register Preference Dataset

```python
from agentic_assistants.training.datasets import TrainingDatasetManager, DatasetFormat

manager = TrainingDatasetManager()
dataset = manager.register(
    name="my-preferences",
    filepath="./data/preferences.json",
    format=DatasetFormat.DPO,
    description="Preference data for alignment",
    tags=["preference", "alignment"],
)
```

### 3. Configure DPO Training

```python
from agentic_assistants.rl import RLConfig, RLMethod, DPOConfig

config = RLConfig(
    # Model settings
    base_model="./outputs/my-sft-model",  # Start from SFT model
    output_name="my-aligned-model",
    
    # Method
    method=RLMethod.DPO,
    preference_dataset_id=dataset.id,
    
    # DPO configuration
    dpo_config=DPOConfig(
        beta=0.1,              # KL penalty strength
        learning_rate=5e-7,    # Lower than SFT
        batch_size=4,
        num_train_epochs=1,
        
        # Optional: use LoRA
        use_lora=True,
        lora_r=8,
        lora_alpha=16,
    ),
    
    # Optimization
    bf16=True,
    gradient_checkpointing=True,
    
    # MLFlow
    mlflow_experiment_name="alignment-experiments",
)
```

### 4. Run DPO Training

```python
from agentic_assistants.rl.adapters import TRLAdapter

adapter = TRLAdapter()
result = await adapter.run_experiment(config)

print(f"Training completed: {result.success}")
print(f"Output model: {result.output_model_path}")
```

## DPO Configuration Guide

### Key Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| beta | KL divergence penalty | 0.05 - 0.5 |
| learning_rate | Learning rate | 1e-7 - 1e-5 |
| max_length | Max sequence length | 512 - 2048 |
| max_prompt_length | Max prompt length | 128 - 512 |
| loss_type | Loss function | sigmoid, hinge, ipo |

### Tips for DPO

1. **Start with lower beta** (0.1) and increase if model diverges too much from base
2. **Use very low learning rate** - DPO is sensitive to learning rate
3. **Quality of preferences matters more than quantity**
4. **Pre-train with SFT first** for best results

## PPO Training

PPO offers more control but requires training a reward model first.

### 1. Train Reward Model

```python
from agentic_assistants.rl import RLConfig, RLMethod, RewardConfig

reward_config = RLConfig(
    base_model="meta-llama/Llama-3.2-3B",
    output_name="reward-model",
    method=RLMethod.REWARD_MODEL,
    preference_dataset_id=dataset.id,
    reward_config=RewardConfig(
        learning_rate=1e-5,
        batch_size=8,
        num_epochs=1,
    ),
)

# Train reward model
adapter = TRLAdapter()
rm_result = await adapter.run_experiment(reward_config)
```

### 2. Run PPO Training

```python
from agentic_assistants.rl import PPOConfig

ppo_config = RLConfig(
    base_model="./outputs/my-sft-model",
    output_name="my-ppo-model",
    method=RLMethod.PPO,
    preference_dataset_id=dataset.id,
    
    ppo_config=PPOConfig(
        learning_rate=1.41e-5,
        batch_size=128,
        mini_batch_size=1,
        ppo_epochs=4,
        
        # PPO-specific
        cliprange=0.2,
        cliprange_value=0.2,
        vf_coef=0.1,
        
        # KL penalty
        init_kl_coef=0.2,
        target_kl=6.0,
        adap_kl_ctrl=True,
        
        # Generation
        max_new_tokens=128,
        temperature=1.0,
    ),
    
    # Reference the reward model
    reward_model_path="./outputs/reward-model",
)

result = await adapter.run_experiment(ppo_config)
```

## Full RLHF Pipeline

For production alignment with human feedback collection:

### 1. Configure RLHF Pipeline

```python
from agentic_assistants.rl import RLHFConfig

rlhf_config = RLConfig(
    base_model="./outputs/my-sft-model",
    output_name="my-rlhf-model",
    method=RLMethod.RLHF,
    preference_dataset_id=dataset.id,
    
    rlhf_config=RLHFConfig(
        # Component configs
        reward_config=RewardConfig(learning_rate=1e-5),
        ppo_config=PPOConfig(learning_rate=1.41e-5),
        
        # Pipeline settings
        train_reward_model=True,
        run_sft=False,  # Set True to include SFT step
        
        # Human feedback settings
        feedback_batch_size=100,
        feedback_iterations=5,
    ),
)
```

### 2. Collect Human Feedback

```python
from agentic_assistants.rl.config import HumanFeedback

# Generate responses for comparison
responses = model.generate_pairs(prompts)

# Collect feedback (integrate with your annotation UI)
feedback = HumanFeedback(
    id="feedback-001",
    prompt="Explain quantum computing",
    response_a=responses[0],
    response_b=responses[1],
    preference=1,  # 1=A preferred, 2=B preferred, 0=tie
    annotator_id="user-123",
)

# Convert to training data
preference_data = feedback.to_preference_data()
```

## Preference Data Best Practices

### Creating High-Quality Preferences

1. **Clear distinction**: Chosen response should be clearly better
2. **Same format**: Both responses should be similarly formatted
3. **Diverse prompts**: Cover many topics and styles
4. **Consistent criteria**: Use clear annotation guidelines

### Data Sources

| Source | Quality | Effort | Scale |
|--------|---------|--------|-------|
| Human annotation | Highest | High | Low |
| GPT-4 as judge | High | Low | High |
| Heuristic rules | Medium | Low | High |
| Existing datasets | Variable | None | High |

### Example: Using LLM as Judge

```python
def create_preference_with_llm_judge(prompt, response_a, response_b, judge_model):
    judge_prompt = f'''Compare these two responses and pick the better one.
    
Prompt: {prompt}

Response A: {response_a}

Response B: {response_b}

Which response is better? Reply with just "A" or "B".'''
    
    judgment = judge_model.generate(judge_prompt)
    
    if "A" in judgment:
        return {"prompt": prompt, "chosen": response_a, "rejected": response_b}
    else:
        return {"prompt": prompt, "chosen": response_b, "rejected": response_a}
```

## Monitoring RL Experiments

### Key Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| reward/mean | Average reward score | Increasing |
| reward/std | Reward variance | Stable |
| kl | KL divergence from base | < target_kl |
| loss/policy | Policy loss | Decreasing |
| loss/value | Value function loss | Decreasing |

### MLFlow Integration

All RL experiments log to MLFlow:
- Training curves
- Reward distributions
- Sample outputs
- Model checkpoints

View at: http://localhost:5000

## Evaluation

### Automated Evaluation

```python
# Compare aligned vs base model
from agentic_assistants.rl.evaluation import compare_models

results = compare_models(
    base_model="./outputs/my-sft-model",
    aligned_model="./outputs/my-aligned-model",
    test_prompts=test_prompts,
    judge_model="gpt-4",
)

print(f"Win rate: {results['win_rate']:.1%}")
```

### Human Evaluation

For production deployments, always include human evaluation:
1. Blind A/B testing
2. Likert scale ratings
3. Task-specific metrics

## REST API

### Start DPO Experiment

```bash
curl -X POST http://localhost:8080/api/v1/rl/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "method": "dpo",
    "base_model": "./outputs/my-sft-model",
    "output_name": "my-aligned-model",
    "preference_dataset_id": "dataset-001",
    "dpo_config": {
      "beta": 0.1,
      "learning_rate": 5e-7
    }
  }'
```

## ORPO Training

ORPO (Odds Ratio Preference Optimization) combines SFT and alignment in a single step, eliminating the need for a reference model and reducing memory usage.

```python
from agentic_assistants.rl import RLConfig, RLMethod
from agentic_assistants.rl.config import ORPOConfig

config = RLConfig(
    base_model="meta-llama/Llama-3.2-1B",
    output_name="my-orpo-model",
    method=RLMethod.ORPO,
    preference_dataset_id=dataset.id,
    orpo_config=ORPOConfig(
        beta=0.1,
        learning_rate=8e-6,
        batch_size=4,
        num_train_epochs=1,
        use_lora=True,
    ),
)

adapter = TRLAdapter()
result = await adapter.train_orpo(config)
```

### When to use ORPO

- You want a simpler pipeline (no separate SFT step)
- Memory is limited (no reference model needed)
- You have preference pairs similar to DPO format

## KTO Training

KTO (Kahneman-Tversky Optimization) works with binary feedback (thumbs up/down) rather than paired preferences.

```python
from agentic_assistants.rl.config import KTOConfig

config = RLConfig(
    base_model="./outputs/my-sft-model",
    output_name="my-kto-model",
    method=RLMethod.KTO,
    preference_dataset_id=dataset.id,
    kto_config=KTOConfig(
        beta=0.1,
        desirable_weight=1.0,
        undesirable_weight=1.0,
        learning_rate=5e-7,
        batch_size=4,
    ),
)

result = await adapter.train_kto(config)
```

### KTO Data Format

KTO expects a dataset with `prompt`, `completion`, and `label` fields where label is a boolean:

```json
[
  {"prompt": "What is ML?", "completion": "Machine learning is ...", "label": true},
  {"prompt": "What is ML?", "completion": "I don't know.", "label": false}
]
```

## SFT (Supervised Fine-Tuning)

SFT is the recommended first step before any RL method. Use TRL's SFTTrainer via the unified adapter:

```python
from agentic_assistants.rl.config import SFTConfig

config = RLConfig(
    base_model="meta-llama/Llama-3.2-1B",
    output_name="my-sft-model",
    method=RLMethod.SFT,
    preference_dataset_id="my-instruct-dataset",
    sft_config=SFTConfig(
        learning_rate=2e-5,
        num_train_epochs=3,
        max_seq_length=2048,
        packing=False,
        use_lora=True,
    ),
)

result = await adapter.train_sft(config)
```

## Distributed Training with Ray

For multi-GPU and cluster training, use the Ray RLlib adapter:

```python
from agentic_assistants.rl.adapters.ray_adapter import RayRLlibAdapter

ray_adapter = RayRLlibAdapter(
    num_workers=4,
    num_gpus=2.0,
    ray_address="auto",  # Connect to existing Ray cluster
)

# Check cluster resources
cluster_info = ray_adapter.get_cluster_info()
print(f"Available GPUs: {cluster_info['cluster_resources']['gpu']}")

# Run distributed PPO
result = await ray_adapter.train_ppo(config, reward_model_path="./reward-model")

# DPO/ORPO/KTO are delegated to TRL but benefit from Ray's data distribution
result = await ray_adapter.run_experiment(config)
```

### Ray Cluster Setup

1. **Local**: Ray auto-initializes with available resources
2. **Existing cluster**: Pass `ray_address="ray://head-node:10001"`
3. **Kubernetes**: Use KubeRay operator for managed clusters

## Adapter Capabilities Comparison

| Feature | TRL | Ray RLlib |
|---------|-----|-----------|
| DPO | Native | Via TRL |
| PPO | Native | Native + distributed |
| ORPO | Native | Via TRL |
| KTO | Native | Via TRL |
| SFT | Native | Via TRL |
| Reward Model | Native | Via TRL |
| Multi-GPU | Via accelerate | Native |
| Cluster | No | Yes |
| LoRA support | Yes | Via TRL |

## Troubleshooting

### Model Degenerates During Training

1. Lower learning rate
2. Increase beta (KL penalty)
3. Check preference data quality
4. Use smaller batch size

### Reward Hacking

1. Add KL penalty (increase beta)
2. Use ensemble of reward models
3. Add rule-based constraints
4. Regular human evaluation

### Training Instability

1. Use gradient clipping
2. Enable adaptive KL control
3. Start with smaller model
4. Verify preference data balance
