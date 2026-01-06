# AI Assistant Index

This folder contains condensed context for LLM copilots working on the **Agentic Assistants** framework. It summarizes architecture, APIs, start/stop procedures, and current modules.

## Structure

```
.index/
├── context/   # Short, LLM-optimized summaries (use these first)
├── cursor/    # Cursor rules & quick context
├── github/    # GitHub Copilot / GH Chat context and file index
└── README.md  # You are here
```

## Current System Highlights (Jan 2026)
- Unified startup: `scripts/start-dev.sh|ps1` (backend + MLFlow + UI: Web UI/Jupyter/Theia). Stop with `scripts/stop-dev.sh|ps1`.
- Web UI (Next.js) lives in `webui/` with pages for Dashboard, Projects, Agents, Flows (YAML import/export), Components, Experiments (MLFlow), Monitoring, Knowledge Bases, Settings.
- Backend now exposes Control Panel APIs: projects, agents, flows, components, notes, tags, stats (`src/agentic_assistants/server/api/`).
- Persistent store for control-panel entities: `core/models.py` (SQLite).
- Repository indexing crew, vector stores (LanceDB/Chroma), embedding providers, agentic patterns (RAG, ReAct, Chain-of-Thought, Collaboration) already integrated.

## Quick Start Commands
- Start everything (default UI=Web UI, port 3000): `./scripts/start-dev.sh`
  - Choose UI: `--ui webui|jupyterlab|theia|none`
  - Stop all: `./scripts/stop-dev.sh`
- Windows PowerShell: `.\\scripts\\start-dev.ps1 -UIChoice webui`
- Web UI only: `./scripts/start-webui.sh --dev` (optional; start-dev covers it)

## Where to look
- Architecture: `.index/context/architecture.md`
- API surface: `.index/context/api-surface.md`
- Patterns: `.index/context/patterns.md`
- Ollama/local LLM tips: `.index/context/ollama-assistant.md`

Keep these files fresh when core modules, APIs, or start/stop flows change.

