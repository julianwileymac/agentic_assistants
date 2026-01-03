# Architecture Overview

This document describes the architecture and design decisions of the Agentic Assistants framework.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Entry Points                                    │
├─────────────────┬─────────────────────┬─────────────────────────────────────┤
│   CLI (Click)   │   Python Imports    │   Startup Scripts (bash/ps1)       │
└────────┬────────┴──────────┬──────────┴─────────────────────────────────────┘
         │                   │
         ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Configuration Layer                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  AgenticConfig  │  │  OllamaSettings │  │  MLFlow/TelemetrySettings   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Core Components                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  OllamaManager  │  │  MLFlowTracker  │  │    TelemetryManager         │  │
│  │  - start/stop   │  │  - experiments  │  │    - tracing                │  │
│  │  - models       │  │  - metrics      │  │    - metrics                │  │
│  │  - chat         │  │  - artifacts    │  │    - spans                  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Framework Adapters                                  │
│  ┌───────────────────────────┐  ┌───────────────────────────────────────┐   │
│  │      CrewAIAdapter        │  │         LangGraphAdapter              │   │
│  │  - create_ollama_agent    │  │  - wrap_node                          │   │
│  │  - run_crew               │  │  - run_graph                          │   │
│  │  - tracking integration   │  │  - stream_graph                       │   │
│  └───────────────────────────┘  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         External Services                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │     Ollama      │  │  MLFlow Server  │  │  OTEL Collector / Jaeger   │  │
│  │  (LLM Runtime)  │  │  (Experiments)  │  │  (Tracing)                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Design

### Configuration (Pydantic Settings)

The configuration system uses Pydantic Settings for:
- Type validation
- Environment variable parsing
- Nested configuration objects
- Default values with documentation

```python
class AgenticConfig(BaseSettings):
    mlflow_enabled: bool = True
    _ollama: OllamaSettings  # Lazy-loaded nested config
```

### Core Components

#### OllamaManager
- Manages Ollama server lifecycle
- Handles model operations (pull, list, delete)
- Provides chat interface
- Cross-platform support (Windows, macOS, Linux)

#### MLFlowTracker
- Context manager for experiment runs
- Runtime enable/disable (no crashes when disabled)
- Decorators for automatic tracking
- Agent-specific logging methods

#### TelemetryManager
- OpenTelemetry SDK initialization
- Span creation with attributes
- Metrics recording
- NoOp implementations when disabled

### Adapters Pattern

Adapters wrap external frameworks with:
1. **Observability integration** - Auto-tracking with MLFlow/OTEL
2. **Convenience methods** - Simplified API for common tasks
3. **Configuration** - Consistent config across frameworks

```python
class BaseAdapter(ABC):
    def __init__(self, config):
        self.tracker = MLFlowTracker(config)
        self.telemetry = TelemetryManager(config)
    
    @contextmanager
    def track_run(self, name):
        # Combined MLFlow + OTEL tracking
        with self.tracker.start_run(name):
            with self.telemetry.span(name):
                yield
```

## Data Flow

### Experiment Tracking Flow

```
User Code → Adapter → MLFlowTracker → MLFlow Server
                   ↘
                    TelemetryManager → OTEL Collector → Jaeger
```

### Agent Execution Flow

```
1. User calls adapter.run_crew(crew, inputs)
2. Adapter starts MLFlow run + OTEL span
3. Adapter executes framework-specific code
4. Framework makes calls to Ollama
5. Results logged to MLFlow as artifacts
6. Metrics recorded to OTEL
7. Run completed, data persisted
```

## Design Decisions

### Why Pydantic Settings?

- Type safety with validation
- Automatic environment variable parsing
- Documentation via Field descriptions
- Nested configuration support

### Why Context Managers?

- Automatic cleanup (end runs, flush telemetry)
- Exception handling without data loss
- Composable (can nest tracking + tracing)
- Familiar Python pattern

### Why Adapters Instead of Monkey Patching?

- Explicit integration (user controls when tracking happens)
- No surprises in production
- Easier to debug
- Framework-independent interface

### Why Optional Docker?

- Lower barrier to entry (local-first)
- Production-ready path available
- Full observability stack when needed
- Works on machines without Docker

## Extension Points

### Adding New Adapters

```python
from agentic_assistants.adapters.base import BaseAdapter

class MyFrameworkAdapter(BaseAdapter):
    def run(self, workflow, inputs):
        with self.track_run("my-workflow"):
            return workflow.execute(inputs)
```

### Custom Telemetry Exporters

```python
# Configure via environment
OTEL_EXPORTER_OTLP_ENDPOINT=http://custom-collector:4317
```

### Custom MLFlow Backend

```python
# Use cloud storage
MLFLOW_TRACKING_URI=databricks://...
MLFLOW_ARTIFACT_LOCATION=s3://bucket/artifacts
```

## Performance Considerations

### Lazy Loading

- Sub-configurations loaded on first access
- MLFlow/OTEL only initialized when used
- Import costs minimized

### Batching

- OpenTelemetry uses BatchSpanProcessor
- MLFlow batches artifact uploads
- Reduces network overhead

### Async Support

- Ollama manager uses httpx (async-capable)
- Future: async adapters for concurrent agents

## Security Considerations

### API Keys

- Never logged or stored in artifacts
- Environment variables only
- Not included in MLFlow parameters

### Local-First

- Default configuration works offline
- No external service dependencies required
- Data stays on your machine

### Container Isolation

- Docker services run in separate network
- Non-root container user
- Read-only config mounts

