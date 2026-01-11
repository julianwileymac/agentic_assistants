# Agentic Assistants - API Surface (Index Context)

## Public Python exports (`agentic_assistants.__all__`)

- `AgenticConfig`
- `OllamaManager`
- `MLFlowTracker`
- `TelemetryManager`
- `Session`
- `SessionManager`
- `AgenticEngine`
- `JupyterWorkspace`
- `workspace`
- `RepositoryIndexingCrew`
- `EmbeddingProvider`
- `RAGPattern`
- `ReActPattern`
- `ChainOfThoughtPattern`
- `CollaborationPattern`
- `track_experiment`
- `get_tracer`
- `__version__`

## Primary CLIs

- `agentic index/search/collections` for vector indexing + search
- `agentic server start` for REST + MCP server
- `agentic context show` for small-context context packs

## Server endpoint groups

- `/api/v1/projects`, `/api/v1/agents`, `/api/v1/flows`, `/api/v1/components`
- `/api/v1/datasources` (+ catalog search/stats)
- `/api/v1/pipelines`
- `/api/v1/kubernetes`
- `/api/v1/training` (training jobs, datasets, export, distillation)
- `/api/v1/models/custom` (custom model registry, deployment)
