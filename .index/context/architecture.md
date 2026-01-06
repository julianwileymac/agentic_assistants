# Architecture Summary (Condensed)

## High-Level
```
User → CLI / Web UI / Notebook
     → FastAPI Backend + WebSocket
     → Core Services (Ollama, MLFlow, OTEL, VectorDB)
     → Agents / Crews / Patterns
```

## Core Modules
- `config.py` — AgenticConfig (Pydantic Settings) for Ollama, MLFlow, Telemetry, VectorDB, Sessions, Server.
- `core/ollama.py` — OllamaManager: ensure/start/stop, list/pull models, chat().
- `core/mlflow_tracker.py` — MLFlowTracker: start_run, log params/metrics/artifacts.
- `core/telemetry.py` — TelemetryManager: OTEL spans/metrics (no-op if disabled).
- `core/models.py` — SQLite store for control-panel entities (projects, agents, flows, components, notes, tags).

## Vector & Indexing
- `vectordb/base.py` — VectorStore ABC + Document/SearchResult.
- Backends: `vectordb/lancedb_store.py`, `vectordb/chroma_store.py`.
- `indexing/codebase.py` — CodebaseIndexer for repos; `indexing/chunker.py` for chunking strategies.
- `crews/repository_indexer.py` — CrewAI-based repo indexing workflow.

## Agents / Patterns
- Adapters: `adapters/base.py`, `adapters/crewai_adapter.py` (+ MLFlow + OTEL).
- Patterns: `patterns/` (RAGPattern, ReActPattern, ChainOfThoughtPattern, CollaborationPattern).
- Embeddings: `embeddings/provider.py` (ollama, sentence-transformers, openai).

## Web UI (Next.js, `webui/`)
- Pages: Dashboard, Projects, Agents, Flows (YAML import/export), Components, Experiments (MLFlow wrapper), Monitoring, Knowledge Bases, Settings.
- Uses Control Panel APIs (`/api/v1/projects|agents|flows|components|notes|tags|stats`).

## Backend API
- Control Panel routers: `server/api/{projects,agents,flows,components,notes,tags}.py`.
- Existing: experiments, artifacts, sessions, data, config.
- Entry: `server/rest.py` (FastAPI factory; includes routers and websocket routes).

## Start / Stop
- Unified: `scripts/start-dev.sh|ps1` (backend + MLFlow + UI choice: webui|jupyterlab|theia|none; default webui). Stop: `scripts/stop-dev.sh|ps1`.
- Helpers: `scripts/start-webui.sh|ps1`, `scripts/start-lab.sh|ps1`.

