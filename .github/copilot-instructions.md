# Agentic Assistants - AI Coding Instructions

This document provides project-specific guidance for AI coding assistants working with the Agentic Assistants framework.

## Project Overview

A local MLOps platform for multi-agent experimentation with CrewAI and LangGraph, using Ollama for local LLM inference. Key goals: learning agentic patterns, cost-effective development, and resource optimization.

## Architecture

```
src/agentic_assistants/
├── config.py           # Pydantic Settings - AgenticConfig is the entry point
├── cli.py              # Click CLI - groups: ollama, mlflow, config, services
├── core/
│   ├── ollama.py       # OllamaManager - server lifecycle + model operations
│   ├── mlflow_tracker.py   # MLFlowTracker - context manager for experiment runs
│   └── telemetry.py    # TelemetryManager - OpenTelemetry spans + metrics
└── adapters/
    ├── base.py         # BaseAdapter - provides track_run() and track_step()
    ├── crewai_adapter.py   # Wraps CrewAI with observability
    └── langgraph_adapter.py # Wraps LangGraph with observability
```

## Key Patterns

### 1. Configuration (Pydantic Settings)
```python
from agentic_assistants import AgenticConfig
config = AgenticConfig()  # Reads from env vars, .env file, or programmatic
config.ollama.host        # Nested access to OllamaSettings
config.mlflow_enabled     # Feature toggle (respects AGENTIC_MLFLOW_ENABLED)
```

### 2. NoOp Pattern for Disabled Features
When `mlflow_enabled=False` or `telemetry_enabled=False`, operations become no-ops without errors:
```python
# In mlflow_tracker.py - all methods check self.enabled first
def log_metric(self, key, value):
    if not self.enabled:
        return  # Silent no-op
```

### 3. Context Manager Tracking
```python
with tracker.start_run(run_name="experiment") as run:
    tracker.log_param("model", "llama3.2")
    # ... run agent code ...
    tracker.log_metric("duration", elapsed)
```

### 4. Adapter Pattern
Adapters in `adapters/` wrap external frameworks:
```python
class CrewAIAdapter(BaseAdapter):
    def run_crew(self, crew, inputs, experiment_name=None):
        with self.track_run(run_name):  # Combined MLFlow + OTEL
            return crew.kickoff(inputs)
```

## Build & Test Commands

```bash
poetry install              # Install dependencies
poetry shell                # Activate venv
pytest                      # Run tests
ruff check src/             # Linting
mypy src/                   # Type checking
agentic --help              # CLI entry point
```

## CLI Structure (Click)

```python
# cli.py uses Click groups
@cli.group()
def ollama(): ...          # agentic ollama start|stop|status|list|pull|delete

@cli.group()
def mlflow(): ...          # agentic mlflow start|ui|status

@cli.group()
def context(): ...         # agentic context show|summary (AI assistant context)

@cli.command()
def run(): ...             # agentic run <script.py> --experiment-name "..."
```

## AI Assistant Context Loading

Use `agentic context` commands to load codebase context for AI assistants:
```bash
agentic context summary                    # Show available context options
agentic context show --task add_adapter    # Load task-specific context
agentic context show --full                # Load full context (8K+ models)
```

## Integration Points

| Component | Port | Purpose |
|-----------|------|---------|
| Ollama | 11434 | LLM inference API |
| MLFlow | 5000 | Experiment tracking UI |
| Jaeger | 16686 | Distributed tracing UI |
| OTEL Collector | 4317 | Telemetry aggregation |

## File Naming Conventions

- `*_adapter.py` - Framework integration wrappers
- `test_*.py` - Pytest test files
- `*.ipynb` - Jupyter notebooks (numbered: `01_`, `02_`, etc.)

## When Adding New Features

1. **New adapter**: Extend `BaseAdapter`, implement `run()`, use `track_run()` for observability
2. **New CLI command**: Add to appropriate Click group in `cli.py`
3. **New config option**: Add to relevant Settings class in `config.py` with `Field(default=..., description=...)`
4. **Tests**: Add to `tests/` with fixtures from `conftest.py`

## Environment Variables

Prefix conventions:
- `AGENTIC_*` - Core framework settings
- `OLLAMA_*` - Ollama configuration  
- `MLFLOW_*` - MLFlow settings
- `OTEL_*` - OpenTelemetry settings

