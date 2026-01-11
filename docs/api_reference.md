# API Reference

This document covers the Python API for the Agentic Assistants framework.

## Core Classes

### AgenticConfig

Central configuration management.

```python
from agentic_assistants import AgenticConfig

# Default configuration (reads from environment/.env)
config = AgenticConfig()

# Override settings
config = AgenticConfig(
    mlflow_enabled=False,
    telemetry_enabled=True,
    log_level="DEBUG",
)

# Access sub-configurations
config.ollama.host          # "http://localhost:11434"
config.ollama.default_model # "llama3.2"
config.mlflow.tracking_uri  # "http://localhost:5000"
config.telemetry.service_name  # "agentic-assistants"

# Export as dictionary
config.to_dict()
```

### OllamaManager

Manage Ollama server and models.

```python
from agentic_assistants import OllamaManager, AgenticConfig

config = AgenticConfig()
ollama = OllamaManager(config)

# Server management
ollama.is_running()          # Check if running
ollama.start()               # Start server
ollama.stop()                # Stop server
ollama.ensure_running()      # Start if not running
ollama.get_status()          # Get detailed status

# Model management
models = ollama.list_models()     # List all models
ollama.pull_model("llama3.2")     # Pull a model
ollama.delete_model("old-model")  # Delete a model
ollama.model_exists("llama3.2")   # Check if model exists
ollama.ensure_model()             # Pull default if missing

# Chat
response = ollama.chat(
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    model="llama3.2",  # Optional, uses default
)

# Context manager
with OllamaManager(config) as ollama:
    response = ollama.chat(messages)
```

### MLFlowTracker

Experiment tracking with MLFlow.

```python
from agentic_assistants.core import MLFlowTracker

tracker = MLFlowTracker(config)

# Start a run
with tracker.start_run(run_name="my-experiment") as run:
    # Log parameters
    tracker.log_param("model", "llama3.2")
    tracker.log_params({"temp": 0.7, "max_tokens": 512})
    
    # Log metrics
    tracker.log_metric("accuracy", 0.95)
    tracker.log_metrics({"loss": 0.05, "duration": 10.5})
    
    # Log artifacts
    tracker.log_artifact("output.txt")
    tracker.log_text("Result text", "output/result.txt")
    tracker.log_dict({"key": "value"}, "config.json")
    
    # Set tags
    tracker.set_tag("experiment_type", "baseline")
    
    # Get run URL
    url = tracker.get_run_url()

# Decorator for automatic tracking
from agentic_assistants.core import track_experiment

@track_experiment("my-experiment", log_args=True)
def my_task(model: str, query: str):
    # Parameters automatically logged
    return process(model, query)
```

### TelemetryManager

OpenTelemetry tracing and metrics.

```python
from agentic_assistants.core import TelemetryManager, get_tracer

telemetry = TelemetryManager(config)
telemetry.initialize()

# Create spans
with telemetry.span("operation-name", attributes={"key": "value"}) as span:
    result = do_work()
    span.set_attribute("result_size", len(result))

# Get tracer for manual instrumentation
tracer = get_tracer("my-component")
with tracer.start_as_current_span("my-span") as span:
    span.add_event("processing-started")
    process()

# Record agent metrics
telemetry.record_agent_metrics(
    agent_name="researcher",
    model="llama3.2",
    duration_seconds=5.2,
    tokens_input=100,
    tokens_output=250,
    success=True,
)

# Decorator for automatic tracing
from agentic_assistants.core import trace_function

@trace_function(attributes={"component": "research"})
def research_topic(topic: str):
    return find_information(topic)
```

## Engine & Workspace

### AgenticEngine

Unified faÃ§ade that wires sessions, vector store, indexing, pipelines, and chat.

```python
from agentic_assistants import AgenticEngine

engine = AgenticEngine()

# Index code and search
engine.index_codebase("./src", collection="agentic")
hits = engine.search("where is the REST server created?", collection="agentic", top_k=5)

# Chat (optionally with RAG)
answer = engine.chat(
    "Summarize the indexing module",
    context_collection="agentic",
    context_top_k=3,
)
```

### JupyterWorkspace

Convenience wrapper for interactive sessions and indexing in notebooks.

```python
from agentic_assistants import JupyterWorkspace

with JupyterWorkspace("my-session") as ws:
    ws.index("./docs")
    results = ws.search("pipelines")
```

## Adapters

### CrewAIAdapter

Integrate CrewAI with observability.

```python
from agentic_assistants.adapters import CrewAIAdapter

adapter = CrewAIAdapter(config)

# Create agents
researcher = adapter.create_ollama_agent(
    role="Research Analyst",
    goal="Find accurate information",
    backstory="Expert researcher...",
    model="llama3.2",  # Optional
)

# Create tasks
task = adapter.create_task(
    description="Research the topic...",
    agent=researcher,
    expected_output="A detailed report",
)

# Create crew
crew = adapter.create_crew(
    agents=[researcher],
    tasks=[task],
    verbose=True,
)

# Run with tracking
result = adapter.run_crew(
    crew,
    inputs={"topic": "AI agents"},
    experiment_name="research-v1",
    run_name="topic-research",
    tags={"type": "research"},
)
```

### LangGraphAdapter

Integrate LangGraph with observability.

```python
from agentic_assistants.adapters import LangGraphAdapter
from typing import TypedDict

class MyState(TypedDict):
    query: str
    result: str

adapter = LangGraphAdapter(config)

# Create LLM
llm = adapter.create_ollama_llm(model="llama3.2")

# Create state graph
graph = adapter.create_state_graph(MyState)

# Wrap nodes for tracing
def my_node(state):
    return {"result": process(state["query"])}

graph.add_node("process", adapter.wrap_node(my_node, "process"))

# Compile and run
workflow = graph.compile()
result = adapter.run_graph(
    workflow,
    inputs={"query": "Hello", "result": ""},
    experiment_name="workflow-v1",
)

# Stream execution
for state in adapter.stream_graph(workflow, inputs):
    print(state)
```

## Knowledge Bases

Use knowledge bases to store/search/query project knowledge.

```python
from agentic_assistants.knowledge import get_knowledge_base

kb = get_knowledge_base("my-project", kb_type="hybrid")
kb.add_documents(["Hello world"], metadatas=[{"source": "demo"}])
results = kb.search("hello", top_k=5)
answer = kb.query("What did we store?")
```

## Pipelines

Kedro-inspired pipeline DAGs with runners.

```python
from agentic_assistants.pipelines import Pipeline, node

def load_data():
    return {"data": [1, 2, 3]}

def summarize(data):
    return {"summary": {"count": len(data)}}

pipe = Pipeline([
    node(load_data, outputs="raw"),
    node(lambda raw: summarize(raw["data"]), inputs="raw", outputs="report"),
])
```

## Server (REST + MCP)

Start the combined server programmatically (or via `agentic server start`).

```python
from agentic_assistants.server.app import start_server

start_server(host="127.0.0.1", port=8080, reload=False)
```

## Utilities

### Logging

```python
from agentic_assistants.utils import setup_logging, get_logger

# Configure logging
setup_logging(level="DEBUG", enable_rich=True)

# Get a logger
logger = get_logger(__name__)
logger.info("Processing started")
logger.debug("Details", extra={"user_id": 123})
```

## Type Definitions

### ModelInfo

Information about an Ollama model.

```python
@dataclass
class ModelInfo:
    name: str
    size: int
    modified_at: str
    digest: str
    
    @property
    def size_gb(self) -> float:
        """Size in gigabytes."""
```

### Exceptions

```python
from agentic_assistants.core.ollama import (
    OllamaError,           # Base exception
    OllamaNotFoundError,   # Ollama not installed
    OllamaConnectionError, # Cannot connect to server
)
```


---

## LLM Training API

### TrainingConfig

Configure LLM training jobs.

```python
from agentic_assistants.training import (
    TrainingConfig,
    TrainingMethod,
    LoRAConfig,
    QLoRAConfig,
)

# Configure a LoRA training job
config = TrainingConfig(
    base_model="meta-llama/Llama-3.2-3B",
    output_name="my-custom-model",
    method=TrainingMethod.LORA,
    lora_config=LoRAConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    ),
    dataset_id="my-dataset",
    num_epochs=3,
    batch_size=4,
    learning_rate=2e-4,
    gradient_accumulation_steps=4,
    bf16=True,
    gradient_checkpointing=True,
)

# QLoRA configuration for memory efficiency
qlora_config = QLoRAConfig(
    r=16,
    lora_alpha=32,
    load_in_4bit=True,
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_quant_type="nf4",
)
```

### TrainingJobManager

Manage training job lifecycle.

```python
from agentic_assistants.training import TrainingJobManager, TrainingJobStatus

manager = TrainingJobManager()

# Create and start a job
job = manager.create_job(config, framework="llama_factory")
manager.start_job(job.id)

# Monitor job status
status = manager.get_job(job.id)
print(f"Status: {status.status}, Progress: {status.progress}")

# Get job logs
logs = manager.get_job_logs(job.id, tail=100)

# List all jobs
jobs = manager.list_jobs(status=TrainingJobStatus.RUNNING)

# Stop a job
await manager.stop_job(job.id)
```

### TrainingDatasetManager

Register and manage training datasets.

```python
from agentic_assistants.training.datasets import TrainingDatasetManager, DatasetFormat

dataset_manager = TrainingDatasetManager()

# Register a local dataset
dataset = dataset_manager.register(
    name="my-instruct-data",
    filepath="./data/train.json",
    format=DatasetFormat.ALPACA,
    description="Custom instruction-following dataset",
    tags=["instruct", "domain-specific"],
)

# Register from HuggingFace
hf_dataset = dataset_manager.register(
    name="alpaca-cleaned",
    hf_dataset_id="yahma/alpaca-cleaned",
    format=DatasetFormat.ALPACA,
)

# List datasets
datasets = dataset_manager.list(format=DatasetFormat.ALPACA)

# Load sample data
samples = dataset.load_samples(limit=10)
```

### Model Export

Export trained models to different formats.

```python
from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat

exporter = ModelExporter()

# Export to GGUF for Ollama
result = exporter.export(
    model_path="./outputs/my-model",
    config=ExportConfig(
        format=ExportFormat.GGUF,
        output_dir="./exports",
        gguf_quantization="q4_k_m",
        merge_lora=True,
    ),
)

# Get supported formats
formats = exporter.get_supported_formats()
quantizations = exporter.get_gguf_quantizations()
```

---

## Reinforcement Learning API

### RLConfig

Configure RL experiments (DPO, PPO, RLHF).

```python
from agentic_assistants.rl import RLConfig, RLMethod, DPOConfig, PPOConfig

# Configure DPO experiment
dpo_config = RLConfig(
    base_model="my-sft-model",
    output_name="my-aligned-model",
    method=RLMethod.DPO,
    preference_dataset_id="preference-data",
    dpo_config=DPOConfig(
        beta=0.1,
        learning_rate=5e-7,
        batch_size=4,
        num_train_epochs=1,
        use_lora=True,
        lora_r=8,
    ),
)

# Configure PPO experiment
ppo_config = RLConfig(
    base_model="my-sft-model",
    output_name="my-ppo-model",
    method=RLMethod.PPO,
    preference_dataset_id="preference-data",
    ppo_config=PPOConfig(
        learning_rate=1.41e-5,
        ppo_epochs=4,
        cliprange=0.2,
        init_kl_coef=0.2,
        target_kl=6.0,
    ),
)
```

### Preference Data

Work with preference data for RLHF/DPO.

```python
from agentic_assistants.rl.config import PreferenceData, HumanFeedback

# Create preference data
preference = PreferenceData(
    prompt="What is the capital of France?",
    chosen="The capital of France is Paris.",
    rejected="France is a country in Europe.",
    chosen_score=0.9,
    rejected_score=0.3,
)

# Collect human feedback
feedback = HumanFeedback(
    id="feedback-001",
    prompt="Explain quantum computing",
    response_a="Quantum computing uses qubits...",
    response_b="Quantum computers are fast...",
    preference=1,  # 1=A preferred, 2=B preferred, 0=tie
    annotator_id="user-123",
)

# Convert feedback to preference data
pref_data = feedback.to_preference_data()
```

---

## Model Serving API

### DeploymentManager

Deploy models to serving backends.

```python
from agentic_assistants.serving import DeploymentManager, ServingBackend

manager = DeploymentManager()

# Deploy to Ollama
deployment = manager.deploy(
    model_path="./outputs/my-model",
    backend=ServingBackend.OLLAMA,
    model_name="my-custom-llm",
    quantization="q4_k_m",  # GGUF quantization
)

# Deploy to vLLM
vllm_deployment = manager.deploy(
    model_path="./outputs/my-model",
    backend=ServingBackend.VLLM,
    model_name="my-model",
    gpu_memory_utilization=0.9,
)

# Check deployment status
status = manager.get_status(deployment.id)

# Undeploy
manager.undeploy(deployment.id)
```

### ServingConfig

Configure serving backends.

```python
from agentic_assistants.serving.config import (
    ServingConfig,
    OllamaConfig,
    VLLMConfig,
    TGIConfig,
)

# Configure Ollama
ollama_config = OllamaConfig(
    host="localhost",
    port=11434,
    num_ctx=4096,
    temperature=0.7,
    default_quantization="q4_k_m",
)

# Configure vLLM
vllm_config = VLLMConfig(
    host="localhost",
    port=8000,
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
    max_num_seqs=256,
)

# Full serving configuration
config = ServingConfig(
    ollama=ollama_config,
    vllm=vllm_config,
    default_backend=ServingBackend.OLLAMA,
)
```

---

## HuggingFace Integration API

### HuggingFaceHubIntegration

Push and pull models from HuggingFace Hub.

```python
from agentic_assistants.integrations.huggingface import (
    HuggingFaceHubIntegration,
    ModelCard,
)

hf = HuggingFaceHubIntegration(token="hf_xxx")

# Push a model
result = hf.push_model(
    model_path="./outputs/my-model",
    repo_id="username/my-model",
    model_card=hf.create_model_card(
        model_name="My Custom Model",
        base_model="meta-llama/Llama-3.2-3B",
        description="Fine-tuned for code generation",
        training_method="lora",
        metrics={"eval_loss": 0.25},
    ),
    private=True,
)

# Pull a model
local_path = hf.pull_model("username/my-model")

# Push a dataset
hf.push_dataset(
    dataset_path="./data/train",
    repo_id="username/my-dataset",
    private=True,
)

# List models
models = hf.list_models(author="username", limit=50)

# Check if model exists
exists = hf.model_exists("username/my-model")
```

---

## Data Observability API

### DataTaggingSystem

Tag and organize training data.

```python
from agentic_assistants.data.training.tagging import DataTaggingSystem, TagCategory

tagging = DataTaggingSystem()

# Create tags
tag = tagging.create_tag(
    name="high_quality",
    category=TagCategory.QUALITY,
    description="High quality, verified data",
    color="#4CAF50",
)

# Assign tags to datasets
tagging.tag_resource(
    tag_id="tag-high-quality",
    resource_type="dataset",
    resource_id="dataset-001",
    confidence=0.95,
)

# Get tags for a resource
tags = tagging.get_resource_tags(
    resource_type="dataset",
    resource_id="dataset-001",
)

# Filter datasets by tag
datasets = tagging.get_resources_by_tag(
    tag_id="tag-high-quality",
    resource_type="dataset",
)
```

### DataLineageTracker

Track data provenance and transformations.

```python
from agentic_assistants.data.training.lineage import (
    DataLineageTracker,
    DataLineageRecord,
)

tracker = DataLineageTracker()

# Record lineage
record = tracker.record(
    model_id="model-001",
    training_job_id="job-001",
    dataset_id="dataset-001",
    dataset_version="1.0.0",
    transformation_steps=[
        {"type": "filter", "criteria": "length > 100"},
        {"type": "deduplicate", "field": "text"},
    ],
    quality_metrics={"avg_length": 256, "unique_ratio": 0.98},
    sample_count=10000,
)

# Get lineage for a model
lineage = tracker.get_model_lineage("model-001")

# Build lineage graph
graph = tracker.build_lineage_graph("model-001")
```

---

## REST API Endpoints

### Training Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/training/jobs | POST | Create a new training job |
| /api/v1/training/jobs | GET | List training jobs |
| /api/v1/training/jobs/{id} | GET | Get job details |
| /api/v1/training/jobs/{id}/status | GET | Get job status |
| /api/v1/training/jobs/{id}/logs | GET | Get job logs |
| /api/v1/training/jobs/{id}/stop | POST | Stop a running job |
| /api/v1/training/datasets | POST | Register a dataset |
| /api/v1/training/datasets | GET | List datasets |
| /api/v1/training/datasets/{id} | GET | Get dataset details |
| /api/v1/training/export | POST | Export a model |
| /api/v1/training/distillation | POST | Start distillation |
| /api/v1/training/frameworks | GET | List available frameworks |
| /api/v1/training/capabilities | GET | Get training capabilities |

### Custom Models Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/models/custom | POST | Register a custom model |
| /api/v1/models/custom | GET | List custom models |
| /api/v1/models/custom/{id} | GET | Get model details |
| /api/v1/models/custom/{id} | PATCH | Update model |
| /api/v1/models/custom/{id} | DELETE | Delete model |
| /api/v1/models/custom/{id}/deploy | POST | Deploy model |
| /api/v1/models/custom/{id}/config | GET | Get training config |
| /api/v1/models/custom/{id}/metrics | GET | Get model metrics |
| /api/v1/models/custom/{id}/tags | POST | Update model tags |

