# Observability & Distributed Tracing

This guide covers the OpenTelemetry tracing, metrics, and log correlation system
built into Agentic Assistants, including the multi-tier backend strategy, offline
trace storage, and integration with MLflow experiment tracking.

## Architecture Overview

Every span created by the framework flows through a single `TelemetryManager`
which resolves the best available backend at startup.

```
Application Code
  │
  ├─ core/telemetry.py  ──  TelemetryManager.span()
  ├─ crews/telemetry.py  ──  CrewTelemetry.trace_*()
  ├─ hooks/implementations.py  ──  TelemetryHook
  └─ data/telemetry.py  ──  trace_operation()
          │
          ▼
   TelemetryManager.initialize()
          │
          ▼
   _resolve_span_exporter()  ── tiered fallback
          │
    ┌─────┼──────────────┐
    ▼     ▼              ▼
  K8s   Docker /      File-based
  OTLP  Standalone    OTLP JSON
  Coll.  Collector    (data/traces/)
    │     │              │
    ▼     ▼              ▼
  Jaeger  Jaeger    TraceStore
                    sync / import
                        │
                        ▼
                   OTLP Collector
```

### Tiered Backend Strategy

`TelemetryManager._resolve_span_exporter()` probes endpoints in order:

| Priority | Condition                  | Exporter                          |
|----------|----------------------------|-----------------------------------|
| 1        | K8s enabled & reachable    | OTLP gRPC to `otel-collector:4317`|
| 2        | Configured endpoint online | OTLP gRPC to `localhost:4317`     |
| 3        | `fallback_to_file = True`  | `FileSpanExporter` (OTLP JSON)    |

Each probe is a TCP connect with a 1-second timeout. The first reachable
endpoint wins. If nothing is reachable and file fallback is disabled, telemetry
is turned off for the session.

## Configuration

All settings live in `TelemetrySettings` (env prefix `OTEL_`).

| Setting                     | Env var                        | Default               | Description                                    |
|-----------------------------|--------------------------------|-----------------------|------------------------------------------------|
| `exporter_otlp_endpoint`    | `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317`| Primary OTLP gRPC endpoint                    |
| `service_name`              | `OTEL_SERVICE_NAME`           | `agentic-assistants`  | Service name in traces                         |
| `fallback_to_file`          | `OTEL_FALLBACK_TO_FILE`       | `true`                | Enable OTLP JSON file fallback                 |
| `file_export_path`          | `OTEL_FILE_EXPORT_PATH`       | `data/traces`         | Directory for file-based trace export          |
| `file_export_format`        | `OTEL_FILE_EXPORT_FORMAT`     | `otlp_json`           | Export format (only `otlp_json` supported)     |

### Python API

```python
from agentic_assistants import AgenticConfig

config = AgenticConfig(telemetry_enabled=True)
# Override via code:
config.telemetry.exporter_otlp_endpoint = "http://my-collector:4317"
config.telemetry.fallback_to_file = True
```

### Environment Variables

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="agentic-assistants"
export OTEL_FALLBACK_TO_FILE="true"
export OTEL_FILE_EXPORT_PATH="data/traces"
```

## Span Conventions

### SpanKind

Every span **must** specify an explicit `SpanKind`. The framework enforces this
by defaulting to `SpanKind.INTERNAL` when callers omit the `kind` parameter.

| SpanKind   | When to use                                          |
|------------|------------------------------------------------------|
| `INTERNAL` | Default. In-process operations (crew runs, tasks)    |
| `CLIENT`   | Outbound calls (LLM API, vector DB, HTTP)            |
| `SERVER`   | Inbound request handling (REST API endpoints)        |
| `PRODUCER` | Async message production (queue publish)             |
| `CONSUMER` | Async message consumption (queue subscribe)          |

### Naming Conventions

Span names follow a dot-separated hierarchy:

```
crew.<crew_name>.run
agent.<agent_name>.execute
task.<task_type>.execute
tool.<tool_name>.call
llm.<model>.<operation>
indexing.<collection>
pipeline_run
node_<node_name>
```

### Attribute Schema

| Attribute               | Type    | Description                    |
|-------------------------|---------|--------------------------------|
| `crew.name`             | string  | Name of the crew               |
| `agent.name`            | string  | Agent identifier               |
| `agent.role`            | string  | Agent role description         |
| `task.type`             | string  | Task category                  |
| `tool.name`             | string  | Tool being invoked             |
| `llm.model`             | string  | LLM model name                 |
| `llm.operation`         | string  | Operation (generate, embed)    |
| `llm.prompt_tokens`     | int     | Input token count              |
| `success`               | bool    | Whether the operation succeeded|
| `duration_seconds`      | float   | Wall-clock duration            |
| `component`             | string  | Subsystem (data, pipeline)     |

## Trace Export / Import

### File-Based Storage

When no OTLP collector is reachable, the `FileSpanExporter` writes each batch
of spans as a timestamped OTLP JSON file:

```
data/traces/
├── traces_20260321T223015_000001_0001.json
├── traces_20260321T223045_000002_0001.json
└── ...
```

Each file contains a complete `ExportTraceServiceRequest` JSON structure:

```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "agentic-assistants"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {"name": "agentic-assistants"},
          "spans": [
            {
              "traceId": "2dc390859af349719eef2ae...",
              "spanId": "272e6d47b53b6f19",
              "name": "crew.indexing.run",
              "kind": 1,
              "startTimeUnixNano": "1774150178000000000",
              "endTimeUnixNano": "1774150188000000000",
              "attributes": [...],
              "events": [],
              "status": {}
            }
          ]
        }
      ]
    }
  ]
}
```

This is the standard OTLP JSON format accepted by any OTLP-compatible backend.

### CLI Commands

```bash
# Show pending trace files
agentic traces status

# Export (backup) to a directory
agentic traces export --output ./traces-backup/

# Import files into a live OTLP collector
agentic traces import --input ./traces-backup/ --endpoint http://localhost:4318

# Import and delete files after success
agentic traces import --input ./traces-backup/ --endpoint http://localhost:4318 --delete

# Sync pending files to auto-detected endpoint
agentic traces sync

# Sync to a specific endpoint
agentic traces sync --endpoint http://otel-collector:4318
```

### Python API

```python
from agentic_assistants.observability.trace_store import TraceStore

store = TraceStore("data/traces")

# Check pending files
print(f"Pending: {store.pending_count()} files")

# Export to backup
store.export_to_file("./backup/traces")

# Import into collector
store.import_from_file("./backup/traces", "http://localhost:4318")

# Sync and delete on success
store.sync_to_collector("http://localhost:4318")
```

### Workflow: Local Development to Kubernetes

1. **Develop locally** without a running collector -- traces are saved to files.
2. **Backup** before deploying: `agentic traces export -o ./traces-backup/`
3. **Deploy** the Kubernetes OTEL stack (see below).
4. **Import** historical traces: `agentic traces import -i ./traces-backup/ -e http://otel-collector:4318`

## Infrastructure Setup

### Docker Compose

The `docker-compose.yml` includes pre-configured OTEL Collector and Jaeger
services:

```bash
docker compose up -d otel-collector jaeger
```

Services:
- **otel-collector** (`localhost:4317` gRPC, `localhost:4318` HTTP, `localhost:8888` Prometheus)
- **jaeger** (`localhost:16686` UI, `localhost:14268` HTTP collector)

Configuration: `docker/otel-collector-config.yaml`

### Kubernetes

Apply the OTEL stack with Kustomize:

```bash
kubectl apply -k k8s/
```

This deploys:
- `otel-collector` Deployment + Service (gRPC :4317, HTTP :4318)
- `jaeger` Deployment + Service (UI :16686)
- ConfigMap with the collector pipeline configuration

The `k8s/configmap.yaml` already sets:
```yaml
OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector:4317"
OTEL_SERVICE_NAME: "agentic-assistants"
```

### Verifying the Stack

```bash
# Docker
curl -s http://localhost:13133/  # Collector health
curl -s http://localhost:16686/api/services | jq .  # Jaeger services

# Kubernetes
kubectl -n agentic port-forward svc/jaeger 16686:16686
kubectl -n agentic port-forward svc/otel-collector 4317:4317 4318:4318
```

## MLflow Integration

MLflow experiment tracking and OpenTelemetry tracing serve complementary roles:

| Aspect       | MLflow                        | OpenTelemetry                  |
|--------------|-------------------------------|--------------------------------|
| Focus        | Experiment results & artifacts| Request-level distributed tracing|
| Granularity  | Per-run (experiment level)    | Per-span (microsecond level)   |
| Storage      | MLflow server / PostgreSQL    | Jaeger / Tempo / file          |
| Use case     | Compare model performance     | Debug latency, trace agent flow|

Both systems are initialized by the framework adapters (`BaseAgenticAdapter`)
and can run simultaneously. The `MLFlowTracker` handles experiment tracking
while `TelemetryManager` handles distributed tracing.

### Correlation

To correlate MLflow runs with traces, the adapters log the OTEL trace ID as an
MLflow run tag:

```python
from agentic_assistants.adapters.base import BaseAgenticAdapter

adapter = BaseAgenticAdapter(config)
with adapter.track_run("my-experiment") as run:
    # Both MLflow run and OTEL spans are active
    result = adapter.execute(task)
```

## Tracing in Code

### Using TelemetryManager

```python
from agentic_assistants.core.telemetry import TelemetryManager

telemetry = TelemetryManager(config)
telemetry.initialize()

with telemetry.span("process-request", {"user_id": "123"}) as span:
    result = process()
    span.set_attribute("result_size", len(result))
```

### Using the Decorator

```python
from agentic_assistants.core.telemetry import trace_function

@trace_function(span_name="fetch-data", attributes={"component": "ingestion"})
def fetch_data(url: str):
    return requests.get(url)
```

### Using CrewTelemetry

```python
from agentic_assistants.crews.telemetry import CrewTelemetry

telemetry = CrewTelemetry(config)

with telemetry.trace_crew_run("research-crew") as span:
    with telemetry.trace_agent_execution("researcher", "Senior Researcher"):
        with telemetry.trace_llm_call("llama3.2", "generate"):
            result = llm.invoke(prompt)
```

### Using Data Telemetry

```python
from agentic_assistants.data.telemetry import trace_operation

with trace_operation("ingest_documents", component="pipeline") as span:
    documents = load_documents()
    span.set_attribute("doc_count", len(documents))
```

## Troubleshooting

### KeyError: None when exporting spans

**Symptom:** `KeyError: None` at `_SPAN_KIND_MAP[sdk_span.kind]`

**Cause:** Spans created without an explicit `SpanKind` default to `None`,
which the OTLP protobuf encoder cannot serialize.

**Fix:** All span creation in the framework now defaults `kind` to
`SpanKind.INTERNAL`. If you create spans directly via the OTel SDK, always
pass `kind`:

```python
tracer.start_as_current_span("my-span", kind=SpanKind.INTERNAL)
```

### No traces appearing in Jaeger

1. Check the collector is running: `curl http://localhost:13133/`
2. Check the endpoint in config: `agentic config show` (look for `OTEL_EXPORTER_OTLP_ENDPOINT`)
3. Check for file fallback: `agentic traces status` -- if traces are going to files, the collector was unreachable at startup
4. Sync file traces: `agentic traces sync`

### Traces going to files instead of collector

The `TelemetryManager` probes the OTLP endpoint at initialization time. If
the collector starts *after* the application, traces will go to files. Either:

- Start the collector first (`docker compose up -d otel-collector`)
- Sync accumulated files later: `agentic traces sync`

### Duplicate TracerProvider warnings

If you see warnings about setting the global `TracerProvider` multiple times,
ensure only one code path initializes the provider. The `TelemetryHook` now
delegates to the global `TelemetryManager` instead of creating its own
provider.

## Metrics

In addition to traces, the framework exports metrics via OTLP:

| Metric                     | Type      | Description                    |
|----------------------------|-----------|--------------------------------|
| `agent.duration`           | Histogram | Agent execution time (seconds) |
| `agent.tokens`             | Counter   | Token usage (input/output)     |
| `agent.requests`           | Counter   | Total agent invocations        |
| `crew.duration`            | Histogram | Crew execution time (seconds)  |
| `crew.tasks.completed`     | Counter   | Completed tasks                |
| `crew.agent.invocations`   | Counter   | Agent invocations within crews |
| `crew.tool.calls`          | Counter   | Tool calls within crews        |
| `crew.tokens`              | Counter   | Token usage within crews       |

Metrics are exported to the same OTLP endpoint as traces. The Prometheus
exporter on the OTEL Collector exposes them at `:8888/metrics`.
