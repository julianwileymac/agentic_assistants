# AI Assistant Index

This folder contains structured indexing files for various AI coding assistants to efficiently analyze and work with the Agentic Assistants codebase.

## Structure

```
.index/
├── github/         # GitHub Copilot / GitHub AI Chat context
├── cursor/         # Cursor AI rules and context
└── context/        # Ollama and local LLM optimized context
```

## Purpose

Each subfolder contains tool-specific files optimized for that assistant's:
- Context window limitations
- Instruction format preferences
- Integration patterns

## Usage

### GitHub Copilot
The main instructions are in `.github/copilot-instructions.md`. The `.index/github/` folder contains extended context for GitHub AI Chat.

### Cursor
Load rules from `.index/cursor/rules.md` into Cursor's project rules.

### Ollama / Local LLMs
Use files in `.index/context/` for condensed context that fits smaller context windows. See `ollama-assistant.md` for usage patterns.

