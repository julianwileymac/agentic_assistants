# Ollama Model Import and Fine-Tuning

This guide covers importing models from Ollama for fine-tuning and exporting customized models back to Ollama.

## Overview

The framework provides a complete pipeline for:

1. **Importing Models** - Export Ollama models for fine-tuning
2. **Fine-Tuning** - Train models on your data
3. **Exporting Models** - Deploy trained models back to Ollama

## Quick Start

### Import a Model

```python
from agentic_assistants.training import OllamaModelImporter

async with OllamaModelImporter() as importer:
    # List available models
    models = await importer.list_available_models()
    for m in models:
        print(f"{m.name}:{m.tag} - {m.size_gb:.2f} GB")
    
    # Import a model
    imported = await importer.import_model("llama3.2")
    print(f"Imported to: {imported.output_path}")
```

### Export a Model

```python
from agentic_assistants.training import OllamaModelExporter

async with OllamaModelExporter() as exporter:
    # Export a fine-tuned model
    exported = await exporter.export_model(
        model_path="./models/fine-tuned",
        name="my-custom-model",
        system_prompt="You are a helpful coding assistant.",
        quantization="q4_k_m"
    )
    print(f"Created Ollama model: {exported.ollama_name}")
```

### Create a Custom Model (No Training)

```python
from agentic_assistants.training import create_custom_ollama_model

# Create a customized model from existing base
model = await create_custom_ollama_model(
    name="my-assistant",
    base_model="llama3.2",
    system_prompt="You are an expert Python developer.",
    parameters={"temperature": 0.7}
)
```

## Model Import Pipeline

### 1. List Available Models

```python
async with OllamaModelImporter() as importer:
    models = await importer.list_available_models()
    
    for m in models:
        print(f"Model: {m.full_name}")
        print(f"  Size: {m.size_gb:.2f} GB")
        print(f"  Family: {m.family}")
        print(f"  Parameters: {m.parameter_size}")
        print(f"  Quantization: {m.quantization}")
```

### 2. Get Model Information

```python
info = await importer.get_model_info("llama3.2")
print(f"Format: {info.format}")
print(f"Digest: {info.digest}")
```

### 3. Import for Fine-Tuning

```python
imported = await importer.import_model(
    model_name="llama3.2",
    output_path=Path("./models/llama3.2"),
    copy_weights=True  # False to create symlink
)

print(f"Name: {imported.name}")
print(f"Source: {imported.source_model}")
print(f"Format: {imported.format}")
print(f"Size: {imported.size_bytes / 1e9:.2f} GB")
```

### 4. Convert to HuggingFace Format

```python
# Convert GGUF to HuggingFace format for training
hf_path = await importer.convert_to_huggingface(imported)
print(f"HuggingFace model at: {hf_path}")
```

### 5. Prepare for Training

```python
training_config = await importer.prepare_for_training(imported)
print(f"Base model: {training_config['base_model']}")
print(f"Model type: {training_config['model_type']}")
```

## Fine-Tuning

After importing, use the training module:

```python
from agentic_assistants.training import TrainingConfig, TrainingJobManager

config = TrainingConfig(
    base_model=training_config['base_model'],
    method="lora",
    dataset_id="my-dataset",
    output_dir="./models/fine-tuned",
)

job_manager = TrainingJobManager()
job = job_manager.create_job(config)
job_manager.start_job(job.id)
```

See the [Training Guide](training.md) for detailed training documentation.

## Model Export Pipeline

### 1. Export Fine-Tuned Model

```python
async with OllamaModelExporter() as exporter:
    exported = await exporter.export_model(
        model_path=Path("./models/fine-tuned"),
        name="my-custom-model",
        system_prompt="You are a helpful assistant.",
        template=None,  # Use default
        parameters={"temperature": 0.7, "top_p": 0.9},
        quantization="q4_k_m"
    )
```

### 2. Available Quantization Methods

| Method | Description | Size | Quality |
|--------|-------------|------|---------|
| `f16` | Full precision | Largest | Best |
| `q8_0` | 8-bit | Large | Very Good |
| `q4_k_m` | 4-bit K-quant medium | Medium | Good (Default) |
| `q4_0` | 4-bit | Small | OK |

### 3. Create from Existing Model

Create a customized model without training:

```python
ollama_name = await exporter.create_from_base(
    name="my-assistant",
    base_model="llama3.2",
    system_prompt="""You are an expert software architect.
You help design clean, maintainable systems.""",
    parameters={
        "temperature": 0.5,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    }
)
```

### 4. Delete a Model

```python
success = await exporter.delete_model("my-custom-model")
```

## API Endpoints

### Ollama Models API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ollama/models` | GET | List all models |
| `/api/v1/ollama/models/{name}` | GET | Get model info |
| `/api/v1/ollama/models/pull` | POST | Pull a model |
| `/api/v1/ollama/models` | DELETE | Delete a model |
| `/api/v1/ollama/models/{name}/import` | POST | Import for training |
| `/api/v1/ollama/models/export` | POST | Export to Ollama |
| `/api/v1/ollama/models/create` | POST | Create custom model |

### Example: Pull a Model

```bash
curl -X POST http://localhost:8080/api/v1/ollama/models/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "llama3.2"}'
```

### Example: Create Custom Model

```bash
curl -X POST http://localhost:8080/api/v1/ollama/models/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-assistant",
    "baseModel": "llama3.2",
    "systemPrompt": "You are a helpful coding assistant.",
    "parameters": {"temperature": 0.7}
  }'
```

## WebUI

Access the Ollama model manager through the WebUI at `/models/ollama`:

- **Available Models**: View and manage local models
- **Pull Models**: Download models from Ollama registry
- **Import for Training**: Prepare models for fine-tuning
- **Create Custom Models**: Create customized models with custom prompts

## Modelfile Configuration

When creating custom models, a Modelfile is generated:

```
FROM llama3.2
SYSTEM "You are a helpful coding assistant."
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

### Supported Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `temperature` | Creativity (0-2) | 0.7 |
| `top_p` | Nucleus sampling | 0.9 |
| `top_k` | Top-k sampling | 40 |
| `repeat_penalty` | Repetition penalty | 1.1 |
| `num_ctx` | Context window | Model default |

## Requirements

- **Ollama** must be installed and running
- **llama.cpp** tools recommended for GGUF conversion
- **transformers >= 4.35** for GGUF loading (optional)

Install conversion tools:

```bash
pip install agentic-assistants[assistant]
```

## Troubleshooting

### Model Not Found

Ensure the model exists in Ollama:
```bash
ollama list
```

### Conversion Failed

Install llama.cpp tools or use the transformers-based conversion:
```bash
pip install transformers>=4.35
```

### Out of Memory

Use a smaller quantization method:
```python
exported = await exporter.export_model(
    model_path=path,
    name="my-model",
    quantization="q4_0"  # Smaller than q4_k_m
)
```

## See Also

- [Framework Assistant](framework_assistant.md) - Built-in assistant
- [Training Guide](training.md) - Detailed training documentation
- [Adapters](adapters.md) - Using models with adapters
