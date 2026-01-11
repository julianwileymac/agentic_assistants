# Agentic Assistants - Patterns (Index Context)

## Python patterns

- Prefer `AgenticEngine` as the main façade for new programmatic integrations.
- Keep configuration in `AgenticConfig` (env + persisted YAML) rather than ad-hoc globals.
- Server code uses FastAPI routers under `src/agentic_assistants/server/api/` and is assembled in `src/agentic_assistants/server/rest.py`.

## UI patterns

- `webui/src/lib/api.ts` is the primary API client. It uses SWR for caching/mutations.
- Backend URL and API key are stored in browser `localStorage`.

## Indexing patterns

- Vector indexing is chunk-based and stored in vector backends (LanceDB/Chroma).
- This `.index/` directory is file-based and model-agnostic: use it for small-context LLM workflows.
