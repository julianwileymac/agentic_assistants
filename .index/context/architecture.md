# Agentic Assistants - Architecture (Index Context)

## High-level

- **CLI** (`agentic ...`): local operations (services, sessions, indexing/search, server)
- **FastAPI server**: REST (`/api/v1/*` + legacy endpoints), WebSocket (`/ws`), MCP (`/mcp`)
- **Web UI Control Panel**: Next.js app in `webui/` consuming the REST APIs
- **AgenticEngine**: programmatic façade (sessions, indexing/search, vector store, pipelines, knowledge)
- **LLM Lifecycle**: training, RL/RLHF, serving, data observability

## Key directories

- `src/agentic_assistants/`: Python framework
- `src/agentic_assistants/server/`: FastAPI REST/WS/MCP
- `src/agentic_assistants/training/`: LLM training (LoRA, QLoRA, full)
- `src/agentic_assistants/rl/`: RL/RLHF (DPO, PPO, RLHF)
- `src/agentic_assistants/serving/`: Model serving (Ollama, vLLM, TGI)
- `src/agentic_assistants/data/training/`: Data observability (tagging, lineage, quality)
- `webui/`: Control Panel UI
- `scripts/`: start/stop helpers + index generation
- `docker-compose.yml`, `docker/`, `k8s/`: infra
