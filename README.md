# 🤖 Agentic Assistants

A local framework for experimenting with multi-agent AI systems, MLOps tooling, and LLMOps best practices.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Agentic Assistants provides a unified platform for:

- **Multi-Agent Experimentation**: Build and test agent teams with CrewAI and LangGraph
- **Local LLM Integration**: Seamless Ollama integration for privacy and control
- **MLOps Integration**: Built-in MLFlow tracking for experiment comparison
- **Observability**: OpenTelemetry tracing and metrics out of the box
- **Learning Platform**: Examples, notebooks, and documentation for exploration

## Features

| Feature | Description |
|---------|-------------|
| **CLI Interface** | Manage Ollama, MLFlow, and run experiments from the command line |
| **Python API** | Import and use directly in your code |
| **CrewAI Adapter** | Build multi-agent teams with role-based collaboration |
| **LangGraph Adapter** | Create stateful workflows with conditional logic |
| **MLFlow Tracking** | Automatic experiment logging, metrics, and artifacts |
| **OpenTelemetry** | Distributed tracing across agent interactions |
| **Docker Support** | Optional containerized infrastructure |

## Quick Start

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.ai)

### Installation

```bash
# Clone the repository
git clone https://github.com/julianwiley/agentic_assistants.git
cd agentic_assistants

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Initialize configuration
agentic config init
```

### Start Services

```bash
# Unix/macOS
./scripts/start.sh

# Windows PowerShell
.\scripts\start.ps1

### JupyterLab (new default IDE)

```bash
# Unix/macOS
./scripts/start-lab.sh

# Windows PowerShell
.\scripts\start-lab.ps1
```

JupyterLab serves on port `3000` by default (config in `lab/jupyter_lab_config.py`). Set `MLFLOW_TRACKING_URI` to point at your MLflow server; notebooks also include the Python MLflow client. A legacy Theia IDE remains available (see Docker Compose profile `theia-ide`).

> Note: Use Python 3.10–3.12 for the lab environment. The start scripts will exit if a newer Python (e.g., 3.14) is active; set `LAB_PYTHON` to an appropriate interpreter (`py -3.11` on Windows).

### Docker Compose

- JupyterLab default IDE: `docker-compose up -d agentic-ide`
- MLflow server: `docker-compose up -d mlflow`
- Legacy Theia (optional): `docker-compose --profile theia up -d theia-ide`

# Or with Docker (includes Jaeger for tracing)
docker-compose up -d
```

### Pull a Model

```bash
agentic ollama pull llama3.2
```

### Run Your First Experiment

```bash
# Simple chat example
agentic run examples/simple_ollama_chat.py

# CrewAI multi-agent example
agentic run examples/crewai_research_team.py

# LangGraph workflow example
agentic run examples/langgraph_workflow.py
```

## Usage

### CLI

```bash
# Ollama management
agentic ollama start              # Start Ollama server
agentic ollama list               # List available models
agentic ollama pull mistral       # Pull a new model

# MLFlow tracking
agentic mlflow start              # Start tracking server
agentic mlflow ui                 # Open MLFlow UI in browser

# Run experiments
agentic run script.py --experiment-name "my-exp"

# Configuration
agentic config show               # View current settings
agentic services status           # Check all services
```

### Python API

```python
from agentic_assistants import AgenticConfig, OllamaManager
from agentic_assistants.adapters import CrewAIAdapter

# Initialize
config = AgenticConfig()
adapter = CrewAIAdapter(config)

# Create an agent
researcher = adapter.create_ollama_agent(
    role="Research Analyst",
    goal="Find accurate information on topics",
    backstory="Expert researcher with years of experience",
)

# Create and run a crew
crew = adapter.create_crew(
    agents=[researcher],
    tasks=[...],
)

result = adapter.run_crew(
    crew,
    inputs={"topic": "AI agents"},
    experiment_name="research-v1",
)
```

### Notebooks

Interactive notebooks for learning:

1. **01_getting_started.ipynb** - Setup verification and basics
2. **02_crewai_basics.ipynb** - Multi-agent teams with CrewAI
3. **03_langgraph_basics.ipynb** - Stateful workflows with LangGraph
4. **04_mlflow_experiments.ipynb** - Experiment tracking and comparison

```bash
# Launch Jupyter
poetry run jupyter notebook notebooks/
```

## Project Structure

```
agentic_assistants/
├── src/agentic_assistants/     # Main package
│   ├── cli.py                  # CLI implementation
│   ├── config.py               # Configuration management
│   ├── core/                   # Core components
│   │   ├── ollama.py           # Ollama manager
│   │   ├── mlflow_tracker.py   # MLFlow integration
│   │   └── telemetry.py        # OpenTelemetry setup
│   ├── adapters/               # Framework adapters
│   │   ├── crewai_adapter.py   # CrewAI integration
│   │   └── langgraph_adapter.py # LangGraph integration
│   └── utils/                  # Utilities
├── examples/                   # Example scripts
├── notebooks/                  # Jupyter notebooks
├── docs/                       # Documentation
├── scripts/                    # Startup/shutdown scripts
├── tests/                      # Test suite
├── docker-compose.yml          # Optional Docker services
└── pyproject.toml              # Project configuration
```

## Configuration

Configuration via environment variables or `.env` file:

```bash
# Core settings
AGENTIC_MLFLOW_ENABLED=true
AGENTIC_LOG_LEVEL=INFO

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2

# MLFlow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=agentic-experiments

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

See [Configuration Guide](docs/configuration.md) for all options.

## Documentation

- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli_reference.md)
- [API Reference](docs/api_reference.md)
- [Configuration](docs/configuration.md)
- [Architecture](docs/architecture.md)

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
pytest

# Linting
ruff check src/

# Type checking
mypy src/
```

## Observability

### MLFlow (Experiment Tracking)

- **URL**: http://localhost:5000
- Compare experiments, view metrics, download artifacts

### Jaeger (Distributed Tracing)

- **URL**: http://localhost:16686 (requires Docker)
- Trace agent interactions, view latencies

## Roadmap

- [ ] Additional agent frameworks (AutoGen, LlamaIndex)
- [ ] Prompt versioning and management
- [ ] Evaluation framework for agent outputs
- [ ] Vector store integrations
- [ ] Web UI for experiment management

## Contributing

Contributions are welcome! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (`pytest`)
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - Stateful workflows
- [Ollama](https://ollama.ai) - Local LLM runtime
- [MLFlow](https://mlflow.org) - Experiment tracking
- [OpenTelemetry](https://opentelemetry.io) - Observability
