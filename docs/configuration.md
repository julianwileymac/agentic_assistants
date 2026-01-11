# Configuration Guide

This guide covers all configuration options for the Agentic Assistants framework.

## Configuration Sources

Configuration is loaded from multiple sources in this order (later sources override earlier):

1. **Default values** - Built into the code
2. **`.env` file** - In the project root
3. **Environment variables** - System or shell variables
4. **Programmatic** - Passed to `AgenticConfig()`

## Environment Variables

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTIC_MLFLOW_ENABLED` | `true` | Enable MLFlow tracking |
| `AGENTIC_TELEMETRY_ENABLED` | `true` | Enable OpenTelemetry |
| `AGENTIC_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `AGENTIC_DATA_DIR` | `./data` | Local data storage directory |

### Ollama Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_DEFAULT_MODEL` | `llama3.2` | Default model for inference |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |

### MLFlow Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLFlow server URL |
| `MLFLOW_EXPERIMENT_NAME` | `agentic-experiments` | Default experiment name |
| `MLFLOW_ARTIFACT_LOCATION` | `None` | Custom artifact storage path |

### OpenTelemetry Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OTLP exporter endpoint |
| `OTEL_SERVICE_NAME` | `agentic-assistants` | Service name in traces |

### Vector DB Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTORDB_BACKEND` | `lancedb` | Vector DB backend (`lancedb`, `chroma`) |
| `VECTORDB_PATH` | `./data/vectors` | Local vector DB storage path |
| `VECTORDB_EMBEDDING_PROVIDER` | `ollama` | Embedding provider (`ollama`, etc.) |
| `VECTORDB_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `VECTORDB_EMBEDDING_DIMENSION` | `768` | Embedding vector dimension |

### Server Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `127.0.0.1` | Server bind host |
| `SERVER_PORT` | `8080` | Server port |
| `SERVER_ENABLE_MCP` | `true` | Enable MCP over WebSocket (`/mcp`) |
| `SERVER_ENABLE_REST` | `true` | Enable REST endpoints |

### Indexing Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `INDEXING_VERSION` | `2.0` | Indexing schema version |
| `INDEXING_CHUNK_SIZE` | `1024` | Chunk size (characters) |
| `INDEXING_CHUNK_OVERLAP` | `128` | Overlap (characters) |
| `INDEXING_MAX_FILE_SIZE_MB` | `1` | Max file size to index |

### Kubernetes Settings (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `K8S_ENABLED` | `false` | Enable Kubernetes integration |
| `K8S_NAMESPACE` | `agentic` | Default namespace |
| `K8S_KUBECONFIG_PATH` | `None` | Optional kubeconfig path |
| `K8S_CONTEXT` | `None` | Optional kubecontext |

### MinIO Settings (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENABLED` | `false` | Enable MinIO integration |
| `MINIO_ENDPOINT` | `minio.data-services.svc.cluster.local:9000` | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `None` | Access key |
| `MINIO_SECRET_KEY` | `None` | Secret key |

## Example .env File

```bash
# =============================================================================
# Agentic Assistants Configuration
# =============================================================================

# Core Settings
AGENTIC_MLFLOW_ENABLED=true
AGENTIC_TELEMETRY_ENABLED=true
AGENTIC_LOG_LEVEL=INFO
AGENTIC_DATA_DIR=./data

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
OLLAMA_TIMEOUT=120

# MLFlow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=agentic-experiments

# OpenTelemetry Configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=agentic-assistants

# Vector DB Configuration
VECTORDB_BACKEND=lancedb
VECTORDB_PATH=./data/vectors
VECTORDB_EMBEDDING_MODEL=nomic-embed-text

# Server Configuration
SERVER_HOST=127.0.0.1
SERVER_PORT=8080

# Optional: Kubernetes
# K8S_ENABLED=false
# K8S_NAMESPACE=agentic

# Optional: MinIO
# MINIO_ENABLED=false
# MINIO_ENDPOINT=localhost:9000
# MINIO_ACCESS_KEY=minioadmin
# MINIO_SECRET_KEY=minioadmin

# Optional: LLM Provider API Keys
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## Programmatic Configuration

```python
from agentic_assistants import AgenticConfig

# Override specific settings
config = AgenticConfig(
    mlflow_enabled=False,
    telemetry_enabled=True,
    log_level="DEBUG",
)

# Access nested settings (read-only)
print(config.ollama.host)
print(config.mlflow.tracking_uri)
print(config.telemetry.service_name)
```

## Configuration Profiles

For different environments, use separate `.env` files:

```bash
# Development
cp env.example .env.development

# Production
cp env.example .env.production

# Load specific profile
export DOTENV_FILE=.env.production
```

Or use environment-specific settings:

```python
import os

if os.environ.get("ENVIRONMENT") == "production":
    config = AgenticConfig(
        mlflow_enabled=True,
        log_level="WARNING",
    )
else:
    config = AgenticConfig(
        mlflow_enabled=True,
        log_level="DEBUG",
    )
```

## Disabling Features at Runtime

### Disable MLFlow Tracking

```bash
# Environment variable
export AGENTIC_MLFLOW_ENABLED=false
agentic run my_script.py

# Or CLI flag
agentic run my_script.py --no-tracking
```

### Disable Telemetry

```bash
export AGENTIC_TELEMETRY_ENABLED=false
```

## Docker Configuration

When using Docker Compose, services are configured via environment:

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - AGENTIC_MLFLOW_ENABLED=true
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

## Validating Configuration

```python
from agentic_assistants import AgenticConfig

config = AgenticConfig()

# Print all settings
import json
print(json.dumps(config.to_dict(), indent=2))

# Or via CLI
agentic config show
agentic config show --json
```

## Best Practices

1. **Never commit `.env`** - Add to `.gitignore`
2. **Use `env.example`** - Document required variables
3. **Validate early** - Check config at startup
4. **Log configuration** - Help with debugging
5. **Use profiles** - Separate dev/staging/prod settings

