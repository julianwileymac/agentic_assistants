# Agentic Assistants - Local LLM Usage Notes

## Typical workflow for small-context local LLMs

1. Load `.index/context/*` as your starting context.
2. Use `.index/surfaces/*` to locate relevant CLI commands, endpoints, and UI routes.
3. Use `.index/symbols/*` to jump to the most relevant files/symbols.
4. Pull the matching `.index/chunks/*` files for the exact implementation details.

## Index location

- This repo stores the model-agnostic index under `.index/`.
