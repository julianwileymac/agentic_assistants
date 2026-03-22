# Nemotron Coding Assistant

Train, fine-tune, and evaluate NVIDIA Nemotron-Nano models on custom curated datasets for coding assistance.

## Quick Start

```python
from examples.nemotron_coding_assistant import NemotronProject

project = NemotronProject()

# 1. Fetch base model weights
project.fetch_model()

# 2. Prepare training dataset
project.prepare_dataset("code-alpaca")

# 3. Fine-tune with QLoRA
project.train(method="qlora")

# 4. Evaluate on coding benchmarks
results = project.evaluate()

# 5. Serve the fine-tuned model
project.serve_model()
```

## Configuration

Edit `config.yaml` to customize model settings, dataset sources, training hyperparameters, and evaluation benchmarks.

## Training Methods

- **SFT** -- Supervised fine-tuning on instruction-response pairs
- **LoRA** -- Low-rank adaptation for parameter-efficient training
- **QLoRA** -- Quantized LoRA for reduced memory usage
- **DPO** -- Direct preference optimization from preference pairs
- **Full** -- Full fine-tuning (requires significant GPU memory)

## Dataset Sources

Configure sources in `config.yaml` under `datasets.sources`. Supported types:
- `huggingface` -- Load from HuggingFace Hub
- `local` -- Load from local files (JSONL, Parquet)
- `url` -- Download from remote URLs
- `s3` -- Load from S3-compatible storage

## Evaluation

Benchmarks: HumanEval, MBPP, and custom coding tasks. Metrics: pass@k, syntax correctness, code style adherence, execution success.

## Project Structure

```
nemotron-coding-assistant/
├── config.yaml          # Project configuration
├── __init__.py          # NemotronProject main class
├── agents/              # Specialized agents
│   ├── coding_agent.py  # Code generation/review
│   ├── dataset_curator.py # Data curation
│   └── eval_agent.py    # Evaluation and reporting
├── datasets/            # Dataset pipeline components
│   ├── sources.py       # Source definitions
│   ├── processing.py    # Cleaning and filtering
│   └── formats.py       # Output format converters
├── training/            # Training configurations
│   ├── configs.py       # Pre-built training configs
│   └── recipes.py       # End-to-end training recipes
├── evaluation/          # Evaluation harness
│   ├── benchmarks.py    # Benchmark runners
│   └── metrics.py       # Coding-specific metrics
└── experiments/         # Scripted experiments
    ├── crew.py          # CrewAI experiment crew
    └── scripts.py       # Standalone experiment scripts
```
