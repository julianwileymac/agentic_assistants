# Agentic Assistants Documentation

Welcome to the Agentic Assistants documentation! This framework provides a local platform for experimenting with multi-agent AI systems, MLOps tooling, and LLMOps practices.

## Overview

Agentic Assistants is designed for:

- **Experimentation**: Explore multi-agent frameworks like CrewAI and LangGraph
- **Learning**: Understand MLOps and LLMOps through hands-on practice
- **Local Development**: Run everything locally with Ollama for privacy and control
- **Observability**: Built-in MLFlow tracking and OpenTelemetry tracing

## Quick Links

- [Installation Guide](installation.md) - Get started quickly
- [CLI Reference](cli_reference.md) - Command-line interface documentation
- [API Reference](api_reference.md) - Python API documentation
- [Configuration](configuration.md) - Configuration options
- [Architecture](architecture.md) - System design overview
- [Server](server.md) - REST + WebSocket + MCP server overview
- [Web UI Control Panel](control_panel_webui.md) - Next.js control panel usage and architecture
- [Indexing & Context](indexing_and_context.md) - Vector indexing/search and `.index/` context packs
- [Pipelines](pipelines.md) - Kedro-inspired pipelines and runners
- [Knowledge Bases](knowledge_bases.md) - Vector/RAG/Hybrid knowledge base APIs
- [Infrastructure](infrastructure.md) - Docker, k8s, MinIO/Redis/Feast integrations
- [Observability & Tracing](observability.md) - OpenTelemetry tracing, metrics, and trace export/import
- [Cookbook](cookbook/index.md) - 30+ recipe pages for local-first RAG/storage/augmentation
- [Notebook Curriculum](../notebooks/README.md) - guided notebook progression including advanced local-first track
- [Learning Path](learning_path.md) - opinionated beginner to advanced progression

## Getting Started

```bash
# Clone the repository
git clone https://github.com/julianwiley/agentic_assistants.git
cd agentic_assistants

# Install dependencies
poetry install

# Start services
./scripts/start-dev.sh  # Linux/macOS/Git Bash
.\scripts\start-dev.ps1  # Windows PowerShell

# Optional: start the Web UI Control Panel
./scripts/start-webui.sh  # Linux/macOS/Git Bash
.\scripts\start-webui.ps1  # Windows PowerShell

# Pull a model
agentic ollama pull llama3.2

# Run an example
agentic run examples/simple_ollama_chat.py
```

## Features

### Multi-Agent Frameworks

- **CrewAI Integration**: Build teams of AI agents with roles and goals
- **LangGraph Integration**: Create stateful workflows with conditional logic

### MLOps Tooling

- **MLFlow Tracking**: Automatic experiment logging and comparison
- **Artifact Storage**: Save prompts, outputs, and configurations
- **Metrics Dashboard**: Visualize performance across experiments

### Observability

- **Distributed Tracing**: Track requests across agents and components
- **Metrics Collection**: Monitor latency, token usage, and success rates
- **Log Correlation**: Connect logs to traces for debugging

### Local-First

- **Ollama Integration**: Manage local LLM models
- **No API Keys Required**: Run experiments without external dependencies
- **Privacy**: Keep your data on your machine

### Server + UI

- **FastAPI Server**: REST APIs, WebSocket streaming (`/ws`), and MCP (`/mcp`)
- **Web UI Control Panel**: Projects, agents, flows, pipelines, knowledge, monitoring, Kubernetes

### Indexing, Knowledge, and Pipelines

- **Indexing/Search**: Chunking + indexing into vector stores (LanceDB/Chroma) via CLI/server
- **Knowledge Bases**: Vector/RAG/Hybrid knowledge base abstractions on top of vector search
- **Pipelines**: Kedro-inspired pipeline DAG + runners + templates (ingestion/monitoring)

## Project Structure

```
agentic_assistants/
├── src/agentic_assistants/    # Main package
│   ├── core/                   # Core components (Ollama, MLFlow, Telemetry)
│   ├── adapters/               # Framework adapters (CrewAI, LangGraph)
│   ├── server/                 # FastAPI REST + WebSocket + MCP server
│   ├── indexing/               # Chunking + codebase indexing
│   ├── knowledge/              # Knowledge base abstractions (vector/rag/hybrid)
│   ├── pipelines/              # Kedro-inspired pipelines + runners + templates
│   ├── kubernetes/             # Kubernetes + storage integrations
│   └── utils/                  # Utilities (logging)
├── examples/                   # Example scripts
│   └── starters/               # Runnable local-first starter projects
├── notebooks/                  # Jupyter notebooks
├── docs/                       # Documentation
│   └── cookbook/               # Recipe-first snippets and implementation guides
├── src/agentic_assistants/templates/  # Packaged template catalog + scaffolding assets
├── webui/                      # Next.js control panel UI
├── k8s/                        # Kubernetes manifests (kustomize)
├── docker/                     # Dockerfiles and OTEL collector config
├── scripts/                    # Startup/shutdown scripts
└── tests/                      # Test suite
```

## Support

- [GitHub Issues](https://github.com/julianwiley/agentic_assistants/issues) - Report bugs and request features
- [Discussions](https://github.com/julianwiley/agentic_assistants/discussions) - Ask questions and share ideas

