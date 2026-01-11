# LLM Training Guide

This guide covers how to train custom LLMs using the Agentic Assistants framework.

## Overview

The training subsystem supports:
- **Full Fine-tuning**: Update all model weights
- **LoRA**: Low-Rank Adaptation for efficient fine-tuning
- **QLoRA**: Quantized LoRA for memory-efficient training
- **Knowledge Distillation**: Transfer knowledge from larger to smaller models

## Prerequisites

- CUDA-capable GPU (recommended: 16GB+ VRAM for LoRA, 24GB+ for full fine-tuning)
- Python 3.10-3.11
- Training dependencies installed: `pip install peft transformers accelerate bitsandbytes`

## Quick Start

### 1. Prepare Your Dataset

Training datasets should be in one of the supported formats:

**Alpaca Format (Instruction-following)**
```json
[
  {
    "instruction": "What is the capital of France?",
    "input": "",
    "output": "The capital of France is Paris."
  }
]
```

**ShareGPT Format (Multi-turn conversation)**
```json
[
  {
    "conversations": [
      {"from": "human", "value": "Hello!"},
      {"from": "gpt", "value": "Hi there! How can I help you today?"}
    ]
  }
]
```

### 2. Register Your Dataset

```python
from agentic_assistants.training.datasets import TrainingDatasetManager, DatasetFormat

manager = TrainingDatasetManager()
dataset = manager.register(
    name="my-training-data",
    filepath="./data/train.json",
    format=DatasetFormat.ALPACA,
    description="Custom instruction-following dataset",
    tags=["instruct", "domain-specific"],
)
print(f"Registered dataset with ID: {dataset.id}")
```

### 3. Configure Training

```python
from agentic_assistants.training import (
    TrainingConfig,
    TrainingMethod,
    LoRAConfig,
)

config = TrainingConfig(
    # Model settings
    base_model="meta-llama/Llama-3.2-3B",
    output_name="my-custom-model",
    
    # Training method
    method=TrainingMethod.LORA,
    lora_config=LoRAConfig(
        r=16,              # LoRA rank
        lora_alpha=32,     # LoRA alpha
        lora_dropout=0.05, # Dropout
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    ),
    
    # Dataset
    dataset_id=dataset.id,
    dataset_format="alpaca",
    max_seq_length=2048,
    
    # Hyperparameters
    num_epochs=3,
    batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    
    # Optimization
    bf16=True,
    gradient_checkpointing=True,
    
    # MLFlow integration
    mlflow_experiment_name="my-training-experiments",
)
```

### 4. Start Training

```python
from agentic_assistants.training import TrainingJobManager

manager = TrainingJobManager()

# Create and start the job
job = manager.create_job(config, framework="llama_factory")
manager.start_job(job.id)

# Monitor progress
import time
while True:
    status = manager.get_job(job.id)
    print(f"Status: {status.status}, Progress: {status.progress:.1%}")
    if status.status in ["completed", "failed"]:
        break
    time.sleep(30)
```

## Training Methods

### LoRA (Low-Rank Adaptation)

LoRA is the recommended method for most use cases. It adds small trainable layers while keeping the base model frozen.

**Advantages:**
- Memory efficient (can train 7B models on 16GB VRAM)
- Fast training
- Easy to merge or swap adapters
- Minimal risk of catastrophic forgetting

**Configuration:**
```python
lora_config = LoRAConfig(
    r=16,                    # Rank (higher = more capacity, more memory)
    lora_alpha=32,           # Scaling factor (typically 2x rank)
    lora_dropout=0.05,       # Regularization
    target_modules=[         # Modules to adapt
        "q_proj", "v_proj",  # Attention
        "k_proj", "o_proj",
        "gate_proj",         # MLP
        "up_proj", "down_proj",
    ],
    bias="none",             # "none", "all", or "lora_only"
)
```

### QLoRA (Quantized LoRA)

QLoRA combines 4-bit quantization with LoRA for even more memory efficiency.

**Advantages:**
- Train 7B models on 8GB VRAM
- Train 13B models on 16GB VRAM
- Similar quality to LoRA with proper hyperparameters

**Configuration:**
```python
from agentic_assistants.training import QLoRAConfig

qlora_config = QLoRAConfig(
    r=16,
    lora_alpha=32,
    load_in_4bit=True,
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

config = TrainingConfig(
    base_model="meta-llama/Llama-3.2-3B",
    output_name="my-qlora-model",
    method=TrainingMethod.QLORA,
    qlora_config=qlora_config,
    # ... other settings
)
```

### Full Fine-tuning

Full fine-tuning updates all model weights. Use for maximum customization when you have sufficient compute.

**Requirements:**
- Multi-GPU setup recommended
- 40GB+ VRAM per GPU for 7B models
- Use gradient checkpointing to reduce memory

**Configuration:**
```python
from agentic_assistants.training import FullFinetuneConfig

full_config = FullFinetuneConfig(
    freeze_embeddings=False,
    gradient_checkpointing=True,
)

config = TrainingConfig(
    base_model="meta-llama/Llama-3.2-3B",
    output_name="my-full-finetune",
    method=TrainingMethod.FULL,
    full_config=full_config,
    # ... other settings
)
```

## Hyperparameter Guide

### Recommended Starting Points

| Parameter | LoRA | QLoRA | Full |
|-----------|------|-------|------|
| Learning Rate | 2e-4 | 2e-4 | 2e-5 |
| Batch Size | 4 | 4 | 4 |
| Gradient Accumulation | 4 | 8 | 8 |
| Epochs | 3 | 3 | 1-2 |
| Warmup Ratio | 0.03 | 0.03 | 0.03 |
| LoRA Rank | 16-64 | 16-64 | N/A |

### Tips for Better Results

1. **Start with lower learning rates** and increase if training is too slow
2. **Monitor loss curves** in MLFlow - look for smooth decrease
3. **Use validation set** to detect overfitting
4. **Gradient accumulation** effectively increases batch size without more memory
5. **Max sequence length** affects memory - start with 1024-2048

## Model Export

After training, export your model for deployment:

### Export to HuggingFace Format

```python
from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat

exporter = ModelExporter()
result = exporter.export(
    model_path="./outputs/my-model",
    config=ExportConfig(
        format=ExportFormat.HUGGINGFACE,
        output_dir="./exports/hf-model",
        merge_lora=True,  # Merge LoRA weights into base model
        include_tokenizer=True,
    ),
)
```

### Export to GGUF for Ollama

```python
result = exporter.export(
    model_path="./outputs/my-model",
    config=ExportConfig(
        format=ExportFormat.GGUF,
        output_dir="./exports/gguf",
        gguf_quantization="q4_k_m",  # Quantization level
        merge_lora=True,
    ),
)
```

### Available GGUF Quantizations

| Quantization | Size | Quality | Speed |
|--------------|------|---------|-------|
| f16 | Largest | Best | Slowest |
| q8_0 | Large | Excellent | Fast |
| q5_k_m | Medium | Very Good | Fast |
| q4_k_m | Small | Good | Fastest |
| q4_0 | Smallest | Acceptable | Fastest |

## Push to HuggingFace Hub

```python
from agentic_assistants.integrations.huggingface import HuggingFaceHubIntegration

hf = HuggingFaceHubIntegration(token="hf_xxx")

result = hf.push_model(
    model_path="./exports/hf-model",
    repo_id="username/my-custom-llm",
    model_card=hf.create_model_card(
        model_name="My Custom LLM",
        base_model="meta-llama/Llama-3.2-3B",
        description="Fine-tuned for domain-specific tasks",
        training_method="lora",
        metrics={"eval_loss": 0.25},
    ),
    private=True,
)
print(f"Model pushed to: {result['url']}")
```

## Monitoring Training

### MLFlow Integration

All training jobs automatically log to MLFlow:
- Parameters (learning rate, batch size, etc.)
- Metrics (loss, eval metrics)
- Checkpoints as artifacts
- Model artifacts

View in MLFlow UI: http://localhost:5000

### Job Logs

```python
# Get training logs
logs = manager.get_job_logs(job.id, tail=100)
for line in logs:
    print(line)
```

## REST API

Training can also be managed via REST API:

**Create Training Job:**
```bash
curl -X POST http://localhost:8080/api/v1/training/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "base_model": "meta-llama/Llama-3.2-3B",
    "output_name": "my-model",
    "method": "lora",
    "dataset_id": "dataset-001",
    "num_epochs": 3,
    "learning_rate": 0.0002
  }'
```

**Get Job Status:**
```bash
curl http://localhost:8080/api/v1/training/jobs/{job_id}/status
```

## Troubleshooting

### Out of Memory (OOM)

1. Reduce batch_size
2. Increase gradient_accumulation_steps
3. Use QLoRA instead of LoRA
4. Reduce max_seq_length
5. Enable gradient_checkpointing

### Training Loss Not Decreasing

1. Check learning rate (might be too low or too high)
2. Verify dataset format is correct
3. Check for data quality issues
4. Try different LoRA rank

### Slow Training

1. Enable bf16 or fp16
2. Use gradient_checkpointing=False (if memory allows)
3. Increase batch_size (if memory allows)
4. Use faster storage for datasets
