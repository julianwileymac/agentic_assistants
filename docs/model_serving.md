# Model Serving Guide

This guide covers how to deploy and serve custom LLMs using the Agentic Assistants framework.

## Overview

The serving subsystem supports multiple deployment backends:
- **Ollama**: Local inference, development, easy setup
- **vLLM**: High-throughput production serving
- **TGI (Text Generation Inference)**: HuggingFace's production server

## Backend Comparison

| Backend | Best For | Setup | Throughput | Memory |
|---------|----------|-------|------------|--------|
| Ollama | Development, local use | Easy | Good | Efficient |
| vLLM | Production, high throughput | Medium | Excellent | Higher |
| TGI | Production, HF ecosystem | Medium | Excellent | Higher |

## Hybrid Hugging Face Execution for Assistant/Testing

Assistant chat and testing/eval flows now support a hybrid provider model:

1. **HF local path** (`huggingface_local`) runs `transformers` inference in-process.
2. **OpenAI-compatible path** (`openai_compatible`) routes to servers like vLLM/TGI/Ollama-proxy.
3. **Legacy Ollama path** (`ollama`) remains default for backward compatibility.

Example environment configuration:

```bash
LLM_PROVIDER=openai_compatible
LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
LLM_OPENAI_BASE_URL=http://localhost:8000/v1
LLM_OPENAI_API_KEY_ENV=OPENAI_API_KEY

# Assistant-specific override (optional)
ASSISTANT_PROVIDER=huggingface_local
ASSISTANT_MODEL=meta-llama/Llama-3.2-3B-Instruct

# Testing/eval override (optional)
TESTING_EVAL_PROVIDER=openai_compatible
TESTING_EVAL_MODEL=meta-llama/Llama-3.1-8B-Instruct
TESTING_EVAL_ENDPOINT=http://localhost:8000/v1
```

Provider/model resolution precedence:

- Request payload override (WebUI/API)
- Assistant/testing defaults
- Global `LLM_*` defaults
- Legacy `OLLAMA_*` defaults

## Quick Start with Ollama

### 1. Export Model to GGUF

Ollama requires models in GGUF format:

```python
from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat

exporter = ModelExporter()
result = exporter.export(
    model_path="./outputs/my-model",
    config=ExportConfig(
        format=ExportFormat.GGUF,
        output_dir="./exports/gguf",
        gguf_quantization="q4_k_m",
        merge_lora=True,
    ),
)

print(f"GGUF model exported to: {result.output_path}")
```

### 2. Deploy to Ollama

```python
from agentic_assistants.serving import DeploymentManager, ServingBackend

manager = DeploymentManager()

deployment = manager.deploy(
    model_path="./exports/gguf/model.gguf",
    backend=ServingBackend.OLLAMA,
    model_name="my-custom-llm",
)

print(f"Model deployed: ollama run {deployment.model_name}")
```

### 3. Use the Model

**Via Ollama CLI:**
```bash
ollama run my-custom-llm
```

**Via Python:**
```python
from agentic_assistants import OllamaManager

ollama = OllamaManager()
response = ollama.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="my-custom-llm",
)
print(response)
```

## GGUF Quantization Options

Choose quantization based on your memory/quality tradeoffs:

| Quantization | Model Size | Quality | Speed | Use Case |
|--------------|------------|---------|-------|----------|
| f16 | 100% | Best | Slower | Quality-critical |
| q8_0 | ~50% | Excellent | Fast | Good balance |
| q6_k | ~40% | Very Good | Fast | Memory-constrained |
| q5_k_m | ~35% | Good | Fast | Recommended default |
| q4_k_m | ~25% | Good | Fastest | Edge devices |
| q4_0 | ~20% | Acceptable | Fastest | Minimal resources |

### Export with Different Quantizations

```python
# High quality
result = exporter.export(model_path, ExportConfig(
    format=ExportFormat.GGUF,
    gguf_quantization="q8_0",
))

# Balanced
result = exporter.export(model_path, ExportConfig(
    format=ExportFormat.GGUF,
    gguf_quantization="q5_k_m",
))

# Small size
result = exporter.export(model_path, ExportConfig(
    format=ExportFormat.GGUF,
    gguf_quantization="q4_k_m",
))
```

## Ollama Modelfile

For custom configurations, create a Modelfile:

```dockerfile
# Modelfile
FROM ./model-q4_k_m.gguf

# System prompt
SYSTEM You are a helpful assistant specialized in code review.

# Parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# Stop sequences
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"
```

Create the model:
```bash
ollama create my-model -f Modelfile
```

## vLLM Deployment

vLLM offers high-throughput serving for production workloads.

### 1. Export to HuggingFace Format

```python
result = exporter.export(
    model_path="./outputs/my-model",
    config=ExportConfig(
        format=ExportFormat.HUGGINGFACE,
        output_dir="./exports/hf-model",
        merge_lora=True,
        include_tokenizer=True,
    ),
)
```

### 2. Start vLLM Server

```python
from agentic_assistants.serving import DeploymentManager, ServingBackend
from agentic_assistants.serving.config import VLLMConfig

manager = DeploymentManager()

deployment = manager.deploy(
    model_path="./exports/hf-model",
    backend=ServingBackend.VLLM,
    model_name="my-model",
    config=VLLMConfig(
        tensor_parallel_size=1,
        gpu_memory_utilization=0.9,
        max_num_seqs=256,
    ),
)
```

**Or via command line:**
```bash
python -m vllm.entrypoints.openai.api_server \
    --model ./exports/hf-model \
    --port 8000 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.9
```

### 3. Use OpenAI-Compatible API

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

response = client.chat.completions.create(
    model="my-model",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## TGI Deployment

HuggingFace's Text Generation Inference for production.

### Docker Deployment

```bash
docker run --gpus all -p 8080:80 \
    -v ./exports/hf-model:/model \
    ghcr.io/huggingface/text-generation-inference \
    --model-id /model \
    --max-input-length 1024 \
    --max-total-tokens 2048
```

### Python Client

```python
from agentic_assistants.serving import DeploymentManager, ServingBackend
from agentic_assistants.serving.config import TGIConfig

deployment = manager.deploy(
    model_path="./exports/hf-model",
    backend=ServingBackend.TGI,
    config=TGIConfig(
        max_input_length=1024,
        max_total_tokens=2048,
        quantize="bitsandbytes",  # Optional quantization
    ),
)
```

## Deployment Management

### Check Deployment Status

```python
# List all deployments
deployments = manager.list_deployments()

for d in deployments:
    print(f"{d.name}: {d.status} ({d.backend})")

# Get specific deployment
status = manager.get_status(deployment.id)
print(f"Status: {status.status}")
print(f"Endpoint: {status.endpoint_url}")
```

### Undeploy

```python
manager.undeploy(deployment.id)
```

### Health Checks

```python
is_healthy = manager.health_check(deployment.id)
print(f"Healthy: {is_healthy}")
```

## Configuration

### Ollama Configuration

```python
from agentic_assistants.serving.config import OllamaConfig

ollama_config = OllamaConfig(
    host="localhost",
    port=11434,
    num_ctx=4096,          # Context window
    num_gpu=-1,            # Auto-detect GPUs
    temperature=0.7,
    top_p=0.9,
    default_quantization="q4_k_m",
)
```

### vLLM Configuration

```python
from agentic_assistants.serving.config import VLLMConfig

vllm_config = VLLMConfig(
    host="localhost",
    port=8000,
    tensor_parallel_size=1,    # GPUs for tensor parallelism
    gpu_memory_utilization=0.9,
    max_num_seqs=256,          # Max concurrent requests
    max_model_len=4096,        # Max sequence length
)
```

### TGI Configuration

```python
from agentic_assistants.serving.config import TGIConfig

tgi_config = TGIConfig(
    host="localhost",
    port=8080,
    max_input_length=1024,
    max_total_tokens=2048,
    max_batch_prefill_tokens=4096,
    quantize="bitsandbytes",  # Optional: bitsandbytes, gptq, awq
    num_shard=1,
)
```

## REST API

### Deploy Model

```bash
curl -X POST http://localhost:8080/api/v1/models/custom/{model_id}/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "target": "ollama",
    "model_name": "my-custom-llm",
    "quantization": "q4_k_m"
  }'
```

### List Deployments

```bash
curl http://localhost:8080/api/v1/deployments
```

## Best Practices

### Development
1. Use Ollama with q4_k_m for fast iteration
2. Test with small context windows first
3. Use verbose logging for debugging

### Production
1. Use vLLM or TGI for high throughput
2. Enable health checks and monitoring
3. Set appropriate GPU memory limits
4. Use load balancing for multiple replicas

### Memory Management
1. Start with lower gpu_memory_utilization (0.8) and increase
2. Monitor for OOM errors
3. Use quantization to reduce memory
4. Consider tensor parallelism for large models

## Monitoring

### Prometheus Metrics (vLLM)

vLLM exposes Prometheus metrics at `/metrics`:
- `vllm:num_requests_running`
- `vllm:num_requests_waiting`
- `vllm:gpu_cache_usage`

### Logging

```python
from agentic_assistants.utils import setup_logging

setup_logging(level="DEBUG")

# Logs include:
# - Deployment status changes
# - Health check results
# - Request latencies
# - Error details
```

## Troubleshooting

### Ollama Model Not Found

1. Check model was created: `ollama list`
2. Verify GGUF file exists and is valid
3. Check Modelfile syntax
4. Try recreating: `ollama rm my-model && ollama create my-model -f Modelfile`

### vLLM Out of Memory

1. Reduce `gpu_memory_utilization`
2. Use smaller `max_num_seqs`
3. Reduce `max_model_len`
4. Use quantization (AWQ, GPTQ)

### TGI Startup Failures

1. Check model format is correct
2. Verify CUDA drivers are installed
3. Check Docker GPU access: `nvidia-smi` inside container
4. Review container logs: `docker logs <container_id>`
