# Agentic Assistants - Cursor Context

## What This Project Does

Agentic Assistants is a local-first framework for experimenting with AI agent systems. It wraps popular agent frameworks (CrewAI, LangGraph) with observability (MLFlow, OpenTelemetry) and provides a unified interface via CLI and Python API.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Package Manager | Poetry |
| CLI | Click + Rich |
| Configuration | Pydantic Settings |
| LLM Runtime | Ollama (local) |
| Agent Frameworks | CrewAI, LangGraph |
| Experiment Tracking | MLFlow |
| Tracing | OpenTelemetry |
| Containers | Docker Compose (optional) |

## Key Abstractions

### AgenticConfig
Central configuration that aggregates all settings. Reads from environment variables and `.env` files.

```python
config = AgenticConfig()
config.mlflow_enabled  # bool
config.ollama.host     # str
config.ollama.default_model  # str
```

### OllamaManager
Manages Ollama server lifecycle and model operations.

```python
ollama = OllamaManager(config)
ollama.ensure_running()
ollama.pull_model("llama3.2")
response = ollama.chat(messages=[...])
```

### Adapters
Wrap agent frameworks with observability:

```python
# CrewAI
adapter = CrewAIAdapter(config)
result = adapter.run_crew(crew, inputs={...}, experiment_name="exp-1")

# LangGraph  
adapter = LangGraphAdapter(config)
result = adapter.run_graph(graph, inputs={...})
```

## Directory Map

```
src/agentic_assistants/
├── __init__.py      # Exports: AgenticConfig, OllamaManager, etc.
├── cli.py           # CLI commands (agentic ...)
├── config.py        # Pydantic configuration classes
├── core/
│   ├── ollama.py    # OllamaManager
│   ├── mlflow_tracker.py  # MLFlowTracker
│   └── telemetry.py # TelemetryManager
├── adapters/
│   ├── base.py      # BaseAdapter (abstract)
│   ├── crewai_adapter.py
│   └── langgraph_adapter.py
└── utils/
    └── logging.py   # setup_logging, get_logger
```

## Common Workflows

### Running experiments
```bash
agentic run examples/crewai_research_team.py --experiment-name "research-v1"
```

### Managing Ollama
```bash
agentic ollama start
agentic ollama pull llama3.2
agentic ollama list
```

### Starting services
```bash
./scripts/start.sh        # Local
docker-compose up -d      # Docker
```

## Integration Points

| Service | Default Port | Config Variable |
|---------|--------------|-----------------|
| Ollama | 11434 | `OLLAMA_HOST` |
| MLFlow | 5000 | `MLFLOW_TRACKING_URI` |
| Jaeger | 16686 | (via Docker) |
| OTEL Collector | 4317 | `OTEL_EXPORTER_OTLP_ENDPOINT` |

