# Core Foundation

The `agentic_assistants.core.foundation` package is the reusable Pythonic core for
future agentic, MLOps, and DataOps enhancements.

It consolidates:

- validated base models and mixins
- explicit DTO boundary tooling
- repository/service abstractions
- plugin registries and serializer backends
- typed state-machine execution primitives
- optional MLOps/DataOps client facades

## Package Layout

```text
src/agentic_assistants/core/foundation/
├── __init__.py
├── base_models.py
├── dto.py
├── repository.py
├── service.py
├── registry.py
├── serialization.py
├── state_machine.py
├── observability.py
├── types.py
├── clients/
│   ├── __init__.py
│   ├── mlops.py
│   └── data.py
└── utils/
    ├── __init__.py
    ├── serialization_utils.py
    ├── metadata.py
    ├── state.py
    └── validation.py
```

## Backward Compatibility

Existing imports from `agentic_assistants.core.*` remain valid. The legacy
modules (`core/base_models.py`, `core/dto.py`, `core/repository.py`, etc.)
now forward to foundation implementations.

## Design Principles

1. **Validation-first**: data boundaries default to explicit typed validation.
2. **Separation of concerns**: entity, DTO, repository, and service layers are distinct.
3. **Optional integrations**: external systems are wrapped behind import-safe facades.
4. **Typed runtime contracts**: protocols replace broad `Any` where practical.

## Quick Examples

### Generic paginated responses

```python
from agentic_assistants.core.foundation import AgenticEntity, PaginatedResponse


class Project(AgenticEntity):
    name: str


payload = PaginatedResponse[Project](items=[Project(name="demo")], total=1)
print(payload.has_next)  # False
```

### DTO conversion with partial updates

```python
from agentic_assistants.core.foundation import BaseDTO, DTOConfig
from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    full_name: str


class UserPatchDTO(BaseDTO[User]):
    class Config(DTOConfig):
        exclude = {"id"}
        partial = True


dto_payload = {"email": "new@example.com"}
user = UserPatchDTO.to_model(dto_payload)  # full_name becomes None for patch semantics
```

### Repository and service layering

```python
from agentic_assistants.core.foundation import (
    AgenticEntity,
    InMemoryRepository,
    BaseService,
)


class Task(AgenticEntity):
    title: str


repo = InMemoryRepository(Task)
service = BaseService(repo)
```

### State machine with checkpointing

```python
from agentic_assistants.core.foundation import (
    START,
    END,
    InMemoryCheckpointer,
    StateMachine,
)


async def step(state):
    return {"count": state.get("count", 0) + 1}


sm = StateMachine()
sm.add_node("step", step).add_edge(START, "step").add_edge("step", END)
graph = sm.compile(checkpointer=InMemoryCheckpointer())
```

## Enhanced Core Modules (v0.2)

The following enhancements are available from `agentic_assistants.core`:

### Async Skills with Retry and Middleware

`BaseSkill.execute()` now honors `SkillConfig.timeout_seconds` and `max_retries`.
Async variants `async_execute()`, `async_route()`, and `async_route_best()` are
available on `AgentController`. Middleware functions can be attached for
cross-cutting concerns:

```python
from agentic_assistants.core import AgentController, SkillMiddleware

def telemetry_mw(skill, payload, result):
    print(f"Skill {result.skill_name}: {result.latency_ms:.1f}ms")
    return result

controller = AgentController(middleware=[telemetry_mw])
```

### RAGAS-Aligned Evaluation Metrics

New metric classes: `ContextRelevance`, `ContextSufficiency`, `AnswerRelevance`,
`CommunicationEfficiency`, `ResourceFootprint`. `EvaluationMixin` now populates
handoff and custom metrics. `GoldenDataset` supports `exact`, `fuzzy`,
`substring`, and `bleu` match modes, and `evolve()` for dataset growth.

### Observer / Subject Pattern

```python
from agentic_assistants.core import Observer, Subject

class MetricLogger(Observer):
    def update(self, event, data=None):
        print(f"[{event}] {data}")

subject = Subject()
subject.attach("epoch_end", MetricLogger())
subject.notify("epoch_end", {"loss": 0.42})
```

### Callable Pipeline and Proxy Patterns

`PipelineBuilder.build()` now returns a `Pipeline` object with `__call__`,
`run()`, and `async_run()` methods. `ProxyBase` and `CachingProxy` support
lazy model loading and prediction caching.

### Performance Utilities

`async_cached` for async function caching, `RateLimiter` for API throttling,
and `BatchProcessor.aprocess(concurrency=N)` for parallel batch processing.

### Validators and Data Utilities

Constrained types (`NonEmptyStr`, `HttpUrl`, `SemVer`, `Slug`, etc.) and
utilities (`chunk_text`, `flatten_dict`, `estimate_tokens`) are now exported
from `agentic_assistants.core`.

## Integration Notes

- Pipeline runners and hook specs now consume typed contracts from
  `core.foundation.types` (catalog and hook manager protocols).
- API DTOs reuse shared paginated/error models from core base models.
- Adapters can standardize run metadata via `AdapterRunMetadata`.
- `RunnableNodeProtocol`, `MutableStateProtocol`, and `StateMapping` are
  now available from the top-level `core` import.

