# `.index/`

This directory contains a **model-agnostic** index of the repo for small-context local LLM workflows.

## Key files

- `manifest.json`: file inventory + chunk inventory
- `context/*`: small context packs (consumed by `ContextLoader` / `agentic context show`)
- `surfaces/*`: CLI commands, REST endpoints, Web UI routes
- `symbols/*`: Python + TS/TSX symbol tables
- `chunks/*`: chunked file contents (Markdown)

## Regenerate

```bash
python scripts/generate_index.py
```
