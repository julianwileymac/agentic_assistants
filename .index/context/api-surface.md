# Public API Surface

## Main Exports (from agentic_assistants)

```python
AgenticConfig      # Central configuration
OllamaManager      # Ollama server/model management
MLFlowTracker      # Experiment tracking
TelemetryManager   # OpenTelemetry tracing
track_experiment   # Decorator for auto-tracking
get_tracer         # Get OTEL tracer instance
```

## Adapters (from agentic_assistants.adapters)

```python
BaseAdapter        # Abstract base class
CrewAIAdapter      # CrewAI integration
LangGraphAdapter   # LangGraph integration
```

## AgenticConfig Properties

```python
config.mlflow_enabled      # bool
config.telemetry_enabled   # bool
config.log_level           # str
config.data_dir            # Path
config.ollama.host         # str
config.ollama.default_model # str
config.ollama.timeout      # int
config.mlflow.tracking_uri # str
config.mlflow.experiment_name # str
config.telemetry.exporter_otlp_endpoint # str
config.telemetry.service_name # str
```

## OllamaManager Methods

```python
manager.is_running() -> bool
manager.start(wait=True, timeout=30) -> bool
manager.stop() -> bool
manager.ensure_running() -> None
manager.list_models() -> list[ModelInfo]
manager.pull_model(name) -> bool
manager.delete_model(name) -> bool
manager.model_exists(name) -> bool
manager.ensure_model(name=None) -> str
manager.chat(messages, model=None) -> dict
manager.get_status() -> dict
```

## MLFlowTracker Methods

```python
tracker.start_run(run_name, tags, nested) -> ContextManager
tracker.log_param(key, value)
tracker.log_params(params_dict)
tracker.log_metric(key, value, step)
tracker.log_metrics(metrics_dict, step)
tracker.log_artifact(local_path, artifact_path)
tracker.log_text(text, artifact_file)
tracker.log_dict(dictionary, artifact_file)
tracker.set_tag(key, value)
tracker.get_run_url() -> str | None
```

## CLI Commands

```
agentic ollama start|stop|status|list|pull|delete
agentic mlflow start|ui|status
agentic config show|init
agentic services start|status
agentic run <script> [--experiment-name] [--no-tracking]
```

