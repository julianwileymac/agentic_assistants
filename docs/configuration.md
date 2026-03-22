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

### Testing Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TESTING_ENABLED` | `true` | Enable testing features |
| `TESTING_SANDBOX_DEFAULT` | `true` | Sandbox tests by default |
| `TESTING_TRACKING_DEFAULT` | `false` | Log tests to MLFlow by default |
| `TESTING_AGENT_EVAL_DEFAULT` | `false` | Enable agent evaluation by default |
| `TESTING_RL_METRICS_DEFAULT` | `false` | Emit RL metrics by default |
| `TESTING_EVAL_PROVIDER` | `None` | Default LLM provider for agent evaluation (`ollama`, `huggingface_local`, `openai_compatible`) |
| `TESTING_EVAL_MODEL` | `None` | Default model for LLM evaluation |
| `TESTING_EVAL_ENDPOINT` | `None` | Optional endpoint override for evaluation calls |
| `TESTING_EVAL_HF_EXECUTION_MODE` | `hybrid` | Evaluation mode for HF local/remote execution |
| `TESTING_TIMEOUT_SECONDS` | `60` | Default test timeout |
| `TESTING_DATASET_SAMPLE_SIZE` | `25` | Default dataset sample size |
| `TESTING_MAX_OUTPUT_CHARS` | `8000` | Output size cap for test results |

### Ollama Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_DEFAULT_MODEL` | `llama3.2` | Default model for inference |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |

### Generic LLM Provider Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | Active provider (`ollama`, `huggingface_local`, `openai_compatible`) |
| `LLM_MODEL` | `None` | Global default chat model |
| `LLM_TIMEOUT` | `120` | Shared chat timeout (seconds) |
| `LLM_OLLAMA_HOST` | `None` | Optional Ollama endpoint override |
| `LLM_OPENAI_BASE_URL` | `http://localhost:8000/v1` | OpenAI-compatible base URL |
| `LLM_OPENAI_API_KEY_ENV` | `OPENAI_API_KEY` | Env var name containing endpoint API key |
| `LLM_HF_EXECUTION_MODE` | `hybrid` | HF execution mode (`local`, `remote`, `hybrid`) |
| `LLM_HF_LOCAL_MODEL` | `None` | Default HF local model id |
| `LLM_HF_DEVICE_MAP` | `auto` | Transformers `device_map` for local inference |
| `LLM_HF_TORCH_DTYPE` | `None` | Optional torch dtype override |
| `LLM_HF_TRUST_REMOTE_CODE` | `false` | Trust remote model code for HF loading |
| `LLM_FALLBACK_PROVIDER` | `None` | Optional fallback provider name |

### Assistant LLM Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSISTANT_PROVIDER` | `ollama` | Assistant-specific provider default |
| `ASSISTANT_MODEL` | `llama3.2` | Assistant default model |
| `ASSISTANT_ENDPOINT` | `None` | Assistant endpoint override |
| `ASSISTANT_OPENAI_API_KEY_ENV` | `OPENAI_API_KEY` | API key env for assistant OpenAI-compatible requests |
| `ASSISTANT_HF_EXECUTION_MODE` | `hybrid` | HF mode for assistant flows |

### MLFlow Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLFlow server URL (auto-uses cluster service if K8S enabled) |
| `MLFLOW_EXPERIMENT_NAME` | `agentic-experiments` | Default experiment name |
| `MLFLOW_ARTIFACT_LOCATION` | `None` | Custom artifact storage path (auto-uses MinIO if enabled) |
| `MLFLOW_BACKEND_STORE_URI` | `None` | PostgreSQL backend store URI (auto-uses POSTGRES_* if enabled) |
| `MLFLOW_S3_ENDPOINT_URL` | `None` | S3/MinIO endpoint URL (auto-uses MINIO_ENDPOINT if enabled) |

When both PostgreSQL and MinIO are enabled, MLflow will automatically use:
- PostgreSQL backend store for metadata and experiment tracking
- MinIO/S3 for artifact storage

This provides centralized persistence for all MLflow runs across the cluster.

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
| `VECTORDB_DEFAULT_SCOPE` | `project` | Default scope (`global`, `user`, `project`, `experiment`) |
| `VECTORDB_ENABLE_CROSS_SCOPE_SEARCH` | `true` | Enable searching across scopes |
| `VECTORDB_TRACK_LINEAGE` | `true` | Track document lineage |

### Redis Cache Settings (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_ENABLED` | `false` | Enable Redis integration |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_PREFIX` | `agentic` | Key prefix for all Redis keys |
| `REDIS_SOLUTION_TTL_HOURS` | `168` | TTL for cached solutions (hours) |
| `REDIS_WORKFLOW_TTL_HOURS` | `24` | TTL for workflow state (hours) |
| `REDIS_SESSION_TTL_HOURS` | `2` | TTL for session data (hours) |
| `REDIS_EMBEDDING_TTL_HOURS` | `24` | TTL for cached embeddings (hours) |

### Embedding Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODE` | `local` | Embedding mode (`local` or `remote`) |
| `EMBEDDING_LOCAL_PROVIDER` | `ollama` | Local provider (`ollama`, `sentence_transformers`) |
| `EMBEDDING_LOCAL_MODEL` | `nomic-embed-text` | Local embedding model |
| `EMBEDDING_REMOTE_PROVIDER` | `openai` | Remote provider (`openai`, `huggingface`, `cohere`) |
| `EMBEDDING_OPENAI_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_BATCH_SIZE` | `32` | Batch size for embedding |
| `EMBEDDING_FALLBACK_TO_LOCAL` | `true` | Fall back to local if remote fails |

### Memory Settings (mem0)

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_BACKEND` | `mem0` | Memory backend |
| `MEMORY_ENABLED` | `true` | Enable agent memory |
| `MEMORY_PERSISTENCE_PATH` | `./data/memory` | Memory storage path |
| `MEMORY_CONTEXT_WINDOW` | `10` | Number of memories for context |
| `MEMORY_MAX_CONTEXT_LENGTH` | `4000` | Maximum context length |

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
| `K8S_KUBECONFIG_PATH` | `None` | Optional kubeconfig path (auto-discovers rpi_kubernetes if not set) |
| `K8S_CONTEXT` | `None` | Optional kubecontext (uses "default" for rpi_kubernetes cluster) |
| `K8S_CLUSTER_ENDPOINT` | `None` | Direct cluster API endpoint (alternative to kubeconfig) |
| `K8S_CLUSTER_TOKEN` | `None` | Bearer token for cluster authentication |
| `K8S_VERIFY_SSL` | `true` | Verify SSL certificates for cluster connections |
| `K8S_AUTODETECT_ENABLED` | `true` | Enable automatic kubeconfig discovery |
| `K8S_AUTODETECT_EXTRA_PATHS` | `""` | Comma-separated list of additional kubeconfig paths to try |
| `K8S_REQUEST_TIMEOUT_SECONDS` | `10` | Request timeout for API calls in seconds |
| `K8S_INSECURE_SKIP_TLS_VERIFY` | `false` | Skip TLS verification (insecure, for testing only) |
| `K8S_PREFER_INCLUSTER` | `auto` | Prefer in-cluster config (auto-detects if running in cluster) |

#### Auto-Discovery

The framework will automatically search for kubeconfig files in this priority order:

1. **Explicit path** (`K8S_KUBECONFIG_PATH` if set)
2. **KUBECONFIG environment variable** (can contain multiple paths separated by `:` or `;`)
3. **rpi_kubernetes discovery** (searches standard repository locations)
4. **Standard locations** (`~/.kube/config` or `%USERPROFILE%\.kube\config` on Windows)
5. **Extra paths** (`K8S_AUTODETECT_EXTRA_PATHS`)

The auto-discovery tries each candidate in order and uses the first one that successfully connects to the cluster API.

#### Troubleshooting

If connection fails, use the diagnostics endpoint to get detailed information:

```bash
curl http://localhost:8080/api/v1/kubernetes/cluster/diagnostics
```

This will show:
- Which kubeconfig candidates were tried
- Specific error messages for each attempt
- Actionable suggestions to fix the issue
- Current capabilities and warnings (for partial connections)

### MinIO Settings (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENABLED` | `false` | Enable MinIO integration |
| `MINIO_ENDPOINT` | `minio.data-services.svc.cluster.local:9000` | MinIO endpoint (rpi_kubernetes cluster default) |
| `MINIO_EXTERNAL_ENDPOINT` | `None` | External MinIO endpoint for access outside cluster |
| `MINIO_ACCESS_KEY` | `minioadmin` | Access key (rpi_kubernetes cluster default) |
| `MINIO_SECRET_KEY` | `minioadmin123` | Secret key (rpi_kubernetes cluster default) |
| `MINIO_SECURE` | `false` | Use HTTPS for MinIO connections |
| `MINIO_DEFAULT_BUCKET` | `agentic-artifacts` | Default bucket for artifact storage |
| `MINIO_MODEL_BUCKET` | `model-cache` | Bucket for cached model files |

### PostgreSQL Settings (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_ENABLED` | `false` | Enable PostgreSQL database integration |
| `POSTGRES_HOST` | `postgresql.data-services.svc.cluster.local` | PostgreSQL server host (rpi_kubernetes cluster) |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_DATABASE` | `mlflow` | Default database name |
| `POSTGRES_USER` | `mlflow` | PostgreSQL user (rpi_kubernetes cluster default) |
| `POSTGRES_PASSWORD` | `mlflow123` | PostgreSQL password (rpi_kubernetes cluster default) |
| `POSTGRES_CONNECTION_STRING` | `None` | Full PostgreSQL connection string (overrides individual settings) |

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

# Optional: Kubernetes (auto-discovers rpi_kubernetes cluster)
# K8S_ENABLED=false
# K8S_NAMESPACE=agentic
# K8S_KUBECONFIG_PATH=
# K8S_CONTEXT=default
# K8S_AUTODETECT_ENABLED=true
# K8S_AUTODETECT_EXTRA_PATHS=
# K8S_REQUEST_TIMEOUT_SECONDS=10
# K8S_INSECURE_SKIP_TLS_VERIFY=false
# K8S_PREFER_INCLUSTER=auto

# Optional: MinIO (configured for rpi_kubernetes cluster)
# MINIO_ENABLED=false
# MINIO_ENDPOINT=minio.data-services.svc.cluster.local:9000
# MINIO_ACCESS_KEY=minioadmin
# MINIO_SECRET_KEY=minioadmin123

# Optional: PostgreSQL (configured for rpi_kubernetes cluster)
# POSTGRES_ENABLED=false
# POSTGRES_HOST=postgresql.data-services.svc.cluster.local
# POSTGRES_PORT=5432
# POSTGRES_DATABASE=mlflow
# POSTGRES_USER=mlflow
# POSTGRES_PASSWORD=mlflow123

# Optional: LLM Provider API Keys
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## Provider/Model Precedence

Provider-aware assistant and testing calls resolve settings in this order:

1. **Request override** (WebUI/API payload fields like `provider`, `model`, `endpoint`)
2. **Assistant/testing defaults** (`ASSISTANT_*`, `TESTING_EVAL_*`)
3. **Global LLM defaults** (`LLM_*`)
4. **Legacy Ollama defaults** (`OLLAMA_*`)

This keeps existing Ollama-first behavior working while allowing per-request/provider routing for hybrid deployments.

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

