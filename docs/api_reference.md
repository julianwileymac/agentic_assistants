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

