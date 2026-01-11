# Installation Guide

This guide covers installing and setting up the Agentic Assistants framework.

## Prerequisites

### Required

- **Python 3.10 or 3.11** (project targets `>=3.10,<3.12`): Download from [python.org](https://python.org)
- **Poetry**: Python package manager
  ```bash
  pip install poetry
  ```
- **Ollama**: Local LLM server
  - Download from [ollama.ai](https://ollama.ai)
  - Or via package managers:
    ```bash
    # macOS
    brew install ollama
    
    # Linux
    curl -fsSL https://ollama.ai/install.sh | sh
    ```

### Optional

- **Docker**: For running MLFlow, Jaeger, and OTEL Collector as containers
  - Download from [docker.com](https://docker.com)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/julianwiley/agentic_assistants.git
cd agentic_assistants
```

### 2. Install Dependencies

```bash
# Install all dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Configure Environment

```bash
# Create configuration file
agentic config init

# Or copy manually
cp env.example .env
```

Edit `.env` to customize settings:

```bash
# Key settings to review:
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
AGENTIC_MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://localhost:5000
```

### 4. Start Services

#### Option A: Local Services (Recommended for Getting Started)

```bash
# Windows PowerShell (recommended)
.\scripts\start-dev.ps1

# Linux/macOS/Git Bash
./scripts/start-dev.sh
```

#### Option A2: Start the Web UI Control Panel (Optional)

```bash
# Windows PowerShell
.\scripts\start-webui.ps1

# Linux/macOS/Git Bash
./scripts/start-webui.sh
```

#### Option A3: Start the API Server Directly (Optional)

```bash
# Start combined REST + MCP server
agentic server start
```

#### Option B: Docker Services (Full Observability Stack)

```bash
docker-compose up -d
```

### 5. Pull a Model

```bash
agentic ollama pull llama3.2
```

### 6. Verify Installation

```bash
# Check CLI
agentic --version

# Check services
agentic services status

# Run a simple example
agentic run examples/simple_ollama_chat.py
```

## Development Installation

For contributing or modifying the framework:

```bash
# Install with dev dependencies
poetry install --with dev

# Run tests
pytest

# Run linting
ruff check src/

# Type checking
mypy src/
```

## Troubleshooting

### Ollama Not Found

```
Error: Ollama executable not found
```

**Solution**: Ensure Ollama is installed and in your PATH. Try running `ollama --version`.

### MLFlow Connection Error

```
Failed to initialize MLFlow
```

**Solution**: Start the MLFlow server with `agentic mlflow start` or disable tracking with `AGENTIC_MLFLOW_ENABLED=false`.

### Port Already in Use

```
Port 5000 is already in use
```

**Solution**: Either stop the conflicting service or change the port in `.env`:
```bash
MLFLOW_TRACKING_URI=http://localhost:5001
```

### Poetry Not Found

```
poetry: command not found
```

**Solution**: Install Poetry:
```bash
pip install poetry
# Or
curl -sSL https://install.python-poetry.org | python3 -
```

## Next Steps

- Explore the [CLI Reference](cli_reference.md)
- Try the [example notebooks](../notebooks/)
- Read the [Architecture Overview](architecture.md)

