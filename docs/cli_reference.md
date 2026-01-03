# CLI Reference

The Agentic Assistants CLI provides commands for managing services and running experiments.

## Global Options

```bash
agentic [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `-v, --verbose` | Enable verbose output |
| `-q, --quiet` | Suppress non-essential output |
| `--help` | Show help message |

## Ollama Commands

Manage Ollama server and models.

### `agentic ollama start`

Start the Ollama server.

```bash
agentic ollama start [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--wait/--no-wait` | `--wait` | Wait for server to be ready |
| `--timeout` | 30 | Seconds to wait for server |

### `agentic ollama stop`

Stop the Ollama server (if started by this tool).

```bash
agentic ollama stop
```

### `agentic ollama status`

Show Ollama server status.

```bash
agentic ollama status
```

### `agentic ollama list`

List available models.

```bash
agentic ollama list
```

### `agentic ollama pull`

Pull a model from the Ollama registry.

```bash
agentic ollama pull MODEL
```

**Examples:**
```bash
agentic ollama pull llama3.2
agentic ollama pull mistral
agentic ollama pull codellama:7b
```

### `agentic ollama delete`

Delete a model from local storage.

```bash
agentic ollama delete MODEL [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y, --yes` | Skip confirmation |

## MLFlow Commands

Manage MLFlow tracking server.

### `agentic mlflow start`

Start the MLFlow tracking server.

```bash
agentic mlflow start [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | 127.0.0.1 | Host to bind to |
| `--port` | 5000 | Port to bind to |
| `--backend-store` | ./mlruns | Backend store URI |

### `agentic mlflow ui`

Open MLFlow UI in browser.

```bash
agentic mlflow ui [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | 5000 | Port where MLFlow is running |

### `agentic mlflow status`

Check MLFlow server status.

```bash
agentic mlflow status [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | 5000 | Port to check |

## Run Commands

### `agentic run`

Run an experiment script with tracking.

```bash
agentic run SCRIPT [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-e, --experiment-name` | MLFlow experiment name |
| `-r, --run-name` | Run name |
| `--no-tracking` | Disable MLFlow tracking |
| `-m, --model` | Override default model |

**Examples:**
```bash
# Basic run
agentic run examples/simple_ollama_chat.py

# With experiment name
agentic run examples/crewai_research_team.py -e "research-v1"

# Without tracking
agentic run my_script.py --no-tracking

# With different model
agentic run my_script.py -m mistral
```

## Config Commands

View and manage configuration.

### `agentic config show`

Show current configuration.

```bash
agentic config show [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

### `agentic config init`

Initialize configuration by creating `.env` file.

```bash
agentic config init [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-f, --force` | Overwrite existing .env file |

## Services Commands

Manage all services together.

### `agentic services start`

Start all required services.

```bash
agentic services start [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--ollama/--no-ollama` | `--ollama` | Start Ollama |
| `--mlflow/--no-mlflow` | `--mlflow` | Start MLFlow |
| `--docker` | False | Use Docker Compose |

**Examples:**
```bash
# Start all locally
agentic services start

# Docker mode (includes Jaeger, OTEL)
agentic services start --docker

# Only Ollama
agentic services start --no-mlflow
```

### `agentic services status`

Show status of all services.

```bash
agentic services status
```

## Environment Variables

The CLI respects these environment variables:

| Variable | Description |
|----------|-------------|
| `AGENTIC_MLFLOW_ENABLED` | Enable/disable MLFlow (`true`/`false`) |
| `AGENTIC_TELEMETRY_ENABLED` | Enable/disable telemetry (`true`/`false`) |
| `AGENTIC_LOG_LEVEL` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `OLLAMA_HOST` | Ollama server URL |
| `OLLAMA_DEFAULT_MODEL` | Default model name |
| `MLFLOW_TRACKING_URI` | MLFlow server URI |
| `MLFLOW_EXPERIMENT_NAME` | Default experiment name |

