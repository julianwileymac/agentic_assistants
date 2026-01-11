# Chunk: fdba26acb888_1

- source: `docs/data_observability.md`
- lines: 102-228
- chunk: 2/5

```
g_resource(
        tag_id="tag-code",
        resource_type=resource_type,
        resource_id=resource_id,
    )
```

## Lineage Tracking

### Recording Lineage

Track how data flows through transformations:

```python
from agentic_assistants.data.training.lineage import (
    DataLineageTracker,
    DataLineageRecord,
)

tracker = DataLineageTracker()

# Record lineage when training a model
record = tracker.record(
    model_id="model-001",
    training_job_id="job-001",
    dataset_id="dataset-001",
    dataset_version="1.0.0",
    dataset_name="my-training-data",
    
    # Transformation history
    transformation_steps=[
        {
            "type": "filter",
            "criteria": "length > 100 and length < 2048",
            "removed_count": 1234,
        },
        {
            "type": "deduplicate",
            "field": "text",
            "method": "minhash",
            "removed_count": 567,
        },
        {
            "type": "clean",
            "operations": ["strip_html", "normalize_unicode"],
        },
    ],
    
    # Quality metrics at training time
    quality_metrics={
        "avg_length": 256,
        "unique_ratio": 0.98,
        "language_distribution": {"en": 0.95, "other": 0.05},
    },
    
    sample_count=10000,
)
```

### Querying Lineage

```python
# Get lineage for a specific model
lineage = tracker.get_model_lineage("model-001")

print(f"Model: {lineage.model_id}")
print(f"Dataset: {lineage.dataset_name} v{lineage.dataset_version}")
print(f"Samples: {lineage.sample_count}")
print("Transformations:")
for step in lineage.transformation_steps:
    print(f"  - {step['type']}")

# Get all models trained on a dataset
models = tracker.get_dataset_usage("dataset-001")
print(f"Dataset used in {len(models)} models")
```

### Building Lineage Graphs

```python
# Build visual lineage graph
graph = tracker.build_lineage_graph("model-001")

# Graph contains:
# - Nodes: datasets, transformations, models
# - Edges: data flow relationships

for node in graph.nodes:
    print(f"Node: {node.id} ({node.type})")

for edge in graph.edges:
    print(f"Edge: {edge.source} -> {edge.target} ({edge.relationship})")
```

### Data Relations

Track relationships between data artifacts:

```python
from agentic_assistants.data.training.lineage import DataRelation

# Record that a dataset was derived from another
tracker.add_relation(
    source_id="raw-dataset",
    source_type="dataset",
    target_id="cleaned-dataset",
    target_type="dataset",
    relationship="derived_from",
    description="Cleaned version with deduplication",
    transformation="dedupe + filter",
)

# Relationship types:
# - derived_from: Target derived from source
# - transforms_to: Source transforms to target
# - subset_of: Target is subset of source
# - merged_from: Target merged from multiple sources
# - trained_on: Model trained on dataset
# - evaluated_on: Model evaluated on dataset
```

## Quality Metrics

### Automated Quality Analysis

```python
```
