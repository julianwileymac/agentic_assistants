# Agentic Assistants - GitHub AI Context

> This file mirrors and extends `.github/copilot-instructions.md` for GitHub AI Chat.

## Project Summary

**Agentic Assistants** is a local MLOps framework for experimenting with multi-agent AI systems. It integrates:
- **Ollama** for local LLM inference
- **CrewAI** and **LangGraph** for multi-agent orchestration
- **MLFlow** for experiment tracking
- **OpenTelemetry** for distributed tracing

## Quick Reference

### Entry Points
| Method | Command/Import |
|--------|---------------|
| CLI | `agentic <command>` |
| Python | `from agentic_assistants import AgenticConfig, OllamaManager` |
| Scripts | `./scripts/start.sh` or `.\scripts\start.ps1` |

### Core Components

```
AgenticConfig          # Central configuration (config.py)
├── OllamaSettings     # Ollama host, model, timeout
├── MLFlowSettings     # Tracking URI, experiment name
└── TelemetrySettings  # OTLP endpoint, service name

OllamaManager          # Server + model management (core/ollama.py)
├── start() / stop()   # Server lifecycle
├── pull_model()       # Download models
└── chat()             # Send chat requests

MLFlowTracker          # Experiment tracking (core/mlflow_tracker.py)
├── start_run()        # Context manager for runs
├── log_param/metric() # Track parameters and metrics
└── log_artifact()     # Store files

TelemetryManager       # OpenTelemetry (core/telemetry.py)
├── span()             # Create trace spans
└── record_agent_metrics()  # Standard agent metrics
```

### Adapters

```python
# CrewAI
adapter = CrewAIAdapter(config)
agent = adapter.create_ollama_agent(role=..., goal=..., backstory=...)
crew = adapter.create_crew(agents=[...], tasks=[...])
result = adapter.run_crew(crew, inputs={...})

# LangGraph
adapter = LangGraphAdapter(config)
llm = adapter.create_ollama_llm()
graph = adapter.create_state_graph(StateClass)
result = adapter.run_graph(graph.compile(), inputs={...})
```

## File Purposes

| File | Purpose |
|------|---------|
| `src/agentic_assistants/__init__.py` | Public API exports |
| `src/agentic_assistants/cli.py` | Click CLI (groups: ollama, mlflow, config, services) |
| `src/agentic_assistants/config.py` | Pydantic Settings configuration |
| `src/agentic_assistants/core/ollama.py` | Ollama server/model management |
| `src/agentic_assistants/core/mlflow_tracker.py` | MLFlow integration |
| `src/agentic_assistants/core/telemetry.py` | OpenTelemetry setup |
| `src/agentic_assistants/adapters/base.py` | BaseAdapter with track_run() |
| `src/agentic_assistants/adapters/crewai_adapter.py` | CrewAI wrapper |
| `src/agentic_assistants/adapters/langgraph_adapter.py` | LangGraph wrapper |

## Common Tasks

### Add a new CLI command
1. Open `src/agentic_assistants/cli.py`
2. Add command under appropriate group (`@ollama.command()`, `@mlflow.command()`, etc.)
3. Use `console.print()` for Rich output

### Add a new adapter
1. Create `src/agentic_assistants/adapters/new_adapter.py`
2. Extend `BaseAdapter`
3. Implement `run()` method
4. Use `self.track_run()` for observability
5. Export from `adapters/__init__.py`

### Add configuration option
1. Add field to appropriate Settings class in `config.py`
2. Use `Field(default=..., description=...)`
3. Document in `env.example`

