# Architecture Summary (Condensed)

## Core Components

```
AgenticConfig → OllamaSettings, MLFlowSettings, TelemetrySettings
OllamaManager → start/stop server, pull/list/delete models, chat()
MLFlowTracker → start_run(), log_param/metric/artifact()
TelemetryManager → span(), record_agent_metrics()
BaseAdapter → track_run(), track_step() [abstract base]
CrewAIAdapter → run_crew(), create_ollama_agent()
LangGraphAdapter → run_graph(), stream_graph(), wrap_node()
```

## Data Flow

```
User → CLI/Python API → Adapter → Core Components → External Services
                              ↓
                        MLFlow Tracking
                        OTEL Tracing
```

## Key Files

| File | Contains |
|------|----------|
| `config.py` | AgenticConfig (Pydantic) |
| `cli.py` | Click commands |
| `core/ollama.py` | OllamaManager |
| `core/mlflow_tracker.py` | MLFlowTracker |
| `core/telemetry.py` | TelemetryManager |
| `adapters/base.py` | BaseAdapter |
| `adapters/crewai_adapter.py` | CrewAI integration |
| `adapters/langgraph_adapter.py` | LangGraph integration |

## Patterns

1. **NoOp**: Check `self.enabled` before operations
2. **Context Managers**: `with tracker.start_run()`, `with telemetry.span()`
3. **Lazy Init**: Sub-configs loaded on first access
4. **Adapter Pattern**: BaseAdapter provides observability wrapper

