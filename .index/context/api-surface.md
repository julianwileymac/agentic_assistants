# Public API Surface (Key Objects)

## Main Exports (`agentic_assistants`)
```python
AgenticConfig
OllamaManager
MLFlowTracker
TelemetryManager
Session, SessionManager
AgenticEngine
JupyterWorkspace, workspace
RepositoryIndexingCrew
EmbeddingProvider
RAGPattern, ReActPattern, ChainOfThoughtPattern, CollaborationPattern
track_experiment
get_tracer
```

## Adapters (`agentic_assistants.adapters`)
```python
BaseAdapter          # abstract
CrewAIAdapter        # CrewAI integration + MLFlow/OTEL
# LangGraph adapter exists but main path is CrewAI
```

## Vector DB (`agentic_assistants.vectordb`)
- `VectorStore.create(backend="lancedb"|"chroma", config, embedding_model)`
- Backends: `LanceDBStore`, `ChromaDBStore`
- Data classes: `Document`, `SearchResult`

## Embeddings (`agentic_assistants.embeddings`)
- Providers: `EmbeddingProvider.create(provider="ollama"|"sentence-transformers"|"openai", model, dimension)`

## Indexing / Crews
- `CodebaseIndexer.index_directory(path, collection, force=True)`
- `RepositoryIndexingCrew.run(repo_path, collection, experiment_name, tags)`

## Control Panel Backend APIs (FastAPI, `server/api`)
- Projects: `GET/POST /api/v1/projects`, `GET/PUT/DELETE /api/v1/projects/{id}`
- Agents: `GET/POST /api/v1/agents`, `GET/PUT/DELETE /api/v1/agents/{id}`, `POST /deploy`, `POST /run`
- Flows: `GET/POST /api/v1/flows`, `GET/PUT/DELETE /api/v1/flows/{id}`, `POST /run`, `GET /validate`
- Components: `GET/POST /api/v1/components`, `GET/PUT/DELETE /api/v1/components/{id}`, `/categories/list`
- Notes: `GET/POST /api/v1/notes`, `GET/PUT/DELETE /api/v1/notes/{id}`
- Tags: `GET /api/v1/tags`, `POST /api/v1/resources/{type}/{id}/tags`, `DELETE /api/v1/resources/{type}/{id}/{tag}`
- Stats: `GET /api/v1/stats`
- Legacy: experiments, artifacts, sessions, data, config

## AgenticConfig (selected)
```python
config.vectordb.backend            # lancedb | chroma
config.vectordb.embedding_model    # default embedding model
config.vectordb.embedding_provider # ollama | sentence-transformers | openai
config.ollama.default_model
config.mlflow.tracking_uri
config.telemetry.exporter_otlp_endpoint
config.data_dir
```

## CLI (existing)
```
agentic ollama start|stop|status|list|pull|delete
agentic mlflow start|ui|status
agentic config show|init
agentic services start|status
agentic run <script> [--experiment-name] [--no-tracking]
```

