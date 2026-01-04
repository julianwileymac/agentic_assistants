# Cursor AI Rules for Agentic Assistants

## Project Context

This is a Python MLOps framework for multi-agent AI experimentation. Uses Poetry for dependencies, Click for CLI, Pydantic for configuration.

## Code Style Rules

1. **Type hints**: Always use type hints for function parameters and return values
2. **Docstrings**: Use Google-style docstrings with Args, Returns, Example sections
3. **Imports**: Group as stdlib, third-party, local with blank lines between
4. **Line length**: 100 characters max (configured in pyproject.toml)

## Architecture Rules

### When creating new adapters:
- Extend `BaseAdapter` from `src/agentic_assistants/adapters/base.py`
- Implement the abstract `run()` method
- Use `self.track_run()` context manager for MLFlow + OTEL tracking
- Use `self.track_step()` for individual operations within a run

### When adding CLI commands:
- Add to appropriate Click group in `cli.py`
- Use `console.print()` with Rich formatting for output
- Handle errors gracefully with informative messages
- Add `--help` descriptions

### When adding configuration:
- Add to appropriate Settings class in `config.py`
- Use `Field(default=..., description="...")` 
- Follow env var naming: `AGENTIC_*`, `OLLAMA_*`, `MLFLOW_*`, `OTEL_*`
- Update `env.example` with new variables

## Pattern References

### NoOp Pattern
```python
def log_metric(self, key: str, value: float) -> None:
    if not self.enabled:
        return  # Silent no-op when disabled
    # ... actual implementation
```

### Context Manager Tracking
```python
with self.tracker.start_run(run_name="my-run") as run:
    self.tracker.log_param("model", model_name)
    result = execute_task()
    self.tracker.log_metric("duration", elapsed)
```

### Adapter Integration
```python
class MyAdapter(BaseAdapter):
    def run(self, workflow, inputs, **kwargs):
        with self.track_run("workflow-run", params={"key": "value"}):
            return workflow.execute(inputs)
```

## File Locations

| Task | Location |
|------|----------|
| Add CLI command | `src/agentic_assistants/cli.py` |
| Add configuration | `src/agentic_assistants/config.py` |
| Add new adapter | `src/agentic_assistants/adapters/` |
| Add core functionality | `src/agentic_assistants/core/` |
| Add tests | `tests/` |
| Add examples | `examples/` |

## Testing

- Use pytest fixtures from `tests/conftest.py`
- Mock external services (Ollama, MLFlow) in tests
- Test both enabled and disabled states for optional features

## Do NOT

- Add unnecessary abstractions for single-use code
- Create new config files (use environment variables)
- Add features without corresponding tests
- Break existing public API without deprecation

