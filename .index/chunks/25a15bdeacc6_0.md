# Chunk: 25a15bdeacc6_0

- source: `docs/pipelines.md`
- lines: 1-51
- chunk: 1/1

```
# Pipelines (Kedro-inspired)

The `agentic_assistants.pipelines` package provides a Kedro-inspired pipeline system:

- **Node**: wraps a callable with named inputs/outputs/tags
- **Pipeline**: a DAG of nodes with validation + topological execution order
- **Runners**: execute a pipeline (sequential/parallel/thread/kubernetes)
- **Templates**: reusable pipeline builders (e.g., ingestion/monitoring)

## Core concepts

### Node + Pipeline

```python
from agentic_assistants.pipelines import Pipeline, node

def load_data():
    return {"rows": [1, 2, 3]}

def summarize(rows):
    return {"count": len(rows)}

pipe = Pipeline([
    node(load_data, outputs="raw"),
    node(lambda raw: summarize(raw["rows"]), inputs="raw", outputs="report"),
])
```

### Runners

Runners implement a common interface (`AbstractRunner`) and produce `PipelineRunResult`:

- `SequentialRunner`
- `ParallelRunner`
- `ThreadRunner`
- `KubernetesRunner` (where configured)

## REST API

The backend exposes pipeline endpoints under:

- `/api/v1/pipelines`

Typical operations:

- list pipelines
- inspect a pipeline (nodes/inputs/outputs)
- run a pipeline and poll status
- visualize a pipeline

```
