# Code Patterns Reference

## 1. Configuration Pattern
```python
from agentic_assistants import AgenticConfig
config = AgenticConfig(mlflow_enabled=False)  # Override
config.ollama.host  # Access nested
```

## 2. NoOp Pattern
```python
def log_metric(self, key, value):
    if not self.enabled:
        return  # Silent when disabled
    mlflow.log_metric(key, value)
```

## 3. Context Manager Tracking
```python
with tracker.start_run(run_name="exp") as run:
    tracker.log_param("model", "llama3.2")
    result = run_experiment()
    tracker.log_metric("accuracy", 0.95)
```

## 4. Adapter Pattern
```python
class NewAdapter(BaseAdapter):
    def run(self, workflow, inputs):
        with self.track_run("run-name"):
            return workflow.execute(inputs)
```

## 5. CLI Command Pattern
```python
@cli.group()
def mygroup(): ...

@mygroup.command("action")
@click.argument("arg")
def mygroup_action(arg):
    console.print(f"[green]Done: {arg}[/green]")
```

## 6. Telemetry Span Pattern
```python
with telemetry.span("operation", attributes={"key": val}) as span:
    result = do_work()
    span.set_attribute("result", result)
```

## 7. Exception Hierarchy
```python
class OllamaError(Exception): ...
class OllamaNotFoundError(OllamaError): ...
class OllamaConnectionError(OllamaError): ...
```

