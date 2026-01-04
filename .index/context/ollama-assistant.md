# Guide for Ollama-Based AI Coding Assistants

This guide helps local LLM-based assistants (using Ollama) work effectively with this codebase.

## Context Loading Strategy

Due to limited context windows in local models, use this priority order:

### Priority 1: Core Understanding (Always Load)
1. `.index/context/architecture.md` - System overview
2. `.index/context/api-surface.md` - Public API reference

### Priority 2: Task-Specific (Load When Needed)
- **Adding features**: `.index/context/patterns.md`
- **Debugging**: Relevant source file + test file
- **CLI work**: `src/agentic_assistants/cli.py`
- **Configuration**: `src/agentic_assistants/config.py`

### Priority 3: Deep Dive (Rarely Needed)
- Full source files from `src/agentic_assistants/`
- Documentation from `docs/`

## Prompt Templates

### For Code Generation
```
Context: [Paste architecture.md]

Task: Create a new adapter for [framework] that:
- Extends BaseAdapter
- Implements run() method
- Uses track_run() for observability

Follow patterns from patterns.md.
```

### For Bug Fixing
```
Context: [Paste relevant source file]
Error: [Paste error message]

Analyze the issue and suggest a fix following project patterns:
- NoOp for disabled features
- Context managers for tracking
- Proper exception handling
```

### For Understanding Code
```
Context: [Paste api-surface.md]

Explain how to use [component] for [task].
Include a working example.
```

## Effective Prompting Tips

1. **Be specific**: Instead of "fix this code", say "fix the type error in the chat() method"
2. **Provide context**: Always include relevant architecture/API info
3. **Reference patterns**: Point to specific patterns from patterns.md
4. **Chunk requests**: Break large tasks into smaller, focused requests

## File Size Considerations

| File | Lines | Load When |
|------|-------|-----------|
| `architecture.md` | ~30 | Always |
| `api-surface.md` | ~80 | Always |
| `patterns.md` | ~50 | Code generation |
| `cli.py` | ~350 | CLI work |
| `config.py` | ~150 | Config work |
| `ollama.py` | ~250 | Ollama work |

## Example Session

```
User: I need to add a new CLI command to check model compatibility.

Assistant response pattern:
1. Load: architecture.md (understand project)
2. Load: cli.py (understand CLI structure)  
3. Generate command following Click pattern
4. Test with: pytest tests/test_cli.py
```

## Token Budget Guidelines

For ~4K context models:
- Load architecture.md (~300 tokens)
- Load api-surface.md (~500 tokens)
- Reserve ~2K for task-specific code
- Reserve ~1K for response

For ~8K+ context models:
- Load all context files
- Include full relevant source files
- More complex multi-file changes possible

