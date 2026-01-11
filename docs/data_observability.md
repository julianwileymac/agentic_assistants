# Data Observability Guide

This guide covers the data tagging, lineage tracking, and quality monitoring features for training data management.

## Overview

The data observability subsystem provides:
- **Data Tagging**: Organize datasets with hierarchical tags
- **Lineage Tracking**: Track data transformations and provenance
- **Quality Metrics**: Monitor data quality throughout the pipeline

## Why Data Observability?

| Challenge | Solution |
|-----------|----------|
| Finding the right training data | Tag-based organization and search |
| Understanding data origins | Lineage tracking |
| Ensuring data quality | Automated quality metrics |
| Reproducibility | Full transformation history |
| Compliance/Governance | Audit trails |

## Data Tagging

### Tag Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| DATA_TYPE | Type of training data | instruct, preference, completion, chat |
| QUALITY | Quality assessment | high_quality, needs_review, verified |
| DOMAIN | Subject domain | code, general, medical, legal |
| SOURCE | Data origin | synthetic, human, curated |
| PROCESSING | Processing status | raw, cleaned, augmented |
| LANGUAGE | Language | en, es, zh, multilingual |
| TASK | Task type | qa, summarization, translation |

### Using the Tagging System

```python
from agentic_assistants.data.training.tagging import (
    DataTaggingSystem,
    TagCategory,
)

tagging = DataTaggingSystem()

# Create a custom tag
tag = tagging.create_tag(
    name="domain_expert_reviewed",
    category=TagCategory.QUALITY,
    description="Reviewed by domain expert",
    color="#4CAF50",  # Green
)

# Assign tag to a dataset
tagging.tag_resource(
    tag_id=tag.id,
    resource_type="dataset",
    resource_id="dataset-001",
    confidence=1.0,  # Certain assignment
    notes="Reviewed by Dr. Smith on 2025-01-10",
)

# Get all tags for a resource
tags = tagging.get_resource_tags(
    resource_type="dataset",
    resource_id="dataset-001",
)

for t in tags:
    print(f"  {t.category}: {t.name}")
```

### Searching by Tags

```python
# Find all high-quality instruction datasets
datasets = tagging.get_resources_by_tag(
    tag_id="tag-high-quality",
    resource_type="dataset",
)

# Find datasets with multiple tags
from agentic_assistants.training.datasets import TrainingDatasetManager

manager = TrainingDatasetManager()
datasets = manager.list(
    tags=["high_quality", "instruct", "code"],
)
```

### Bulk Tagging

```python
# Tag multiple resources at once
resources = [
    ("dataset", "dataset-001"),
    ("dataset", "dataset-002"),
    ("dataset", "dataset-003"),
]

for resource_type, resource_id in resources:
    tagging.tag_resource(
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
from agentic_assistants.data.training.quality import DataQualityAnalyzer

analyzer = DataQualityAnalyzer()

# Analyze a dataset
metrics = analyzer.analyze("./data/train.json")

print(f"Total samples: {metrics['total_samples']}")
print(f"Average length: {metrics['avg_length']}")
print(f"Unique ratio: {metrics['unique_ratio']:.2%}")
print(f"Language distribution: {metrics['language_distribution']}")

# Quality issues
if metrics['issues']:
    print("Issues found:")
    for issue in metrics['issues']:
        print(f"  - {issue['type']}: {issue['description']}")
```

### Quality Checks

| Check | Description | Threshold |
|-------|-------------|-----------|
| Duplicates | Exact and near-duplicates | < 5% |
| Length | Sample length distribution | Configurable |
| Language | Language consistency | > 95% target |
| Format | Schema validation | 100% valid |
| Content | PII, toxicity detection | 0% issues |

### Custom Quality Rules

```python
from agentic_assistants.data.training.quality import QualityRule

# Define custom rule
rule = QualityRule(
    name="min_instruction_length",
    description="Instruction must be at least 10 characters",
    check=lambda sample: len(sample.get("instruction", "")) >= 10,
    severity="warning",
)

analyzer.add_rule(rule)

# Run analysis with custom rules
metrics = analyzer.analyze("./data/train.json", custom_rules=[rule])
```

## Database Schema

The data observability system uses SQLite tables:

### data_tags

Stores tag definitions:
```sql
CREATE TABLE data_tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    color TEXT,
    created_at TEXT,
    usage_count INTEGER
);
```

### dataset_tags

Tag assignments:
```sql
CREATE TABLE dataset_tags (
    id TEXT PRIMARY KEY,
    tag_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    confidence REAL,
    notes TEXT,
    assigned_at TEXT
);
```

### data_lineage

Lineage records:
```sql
CREATE TABLE data_lineage (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    training_job_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_version TEXT,
    transformation_steps TEXT,  -- JSON
    quality_metrics TEXT,       -- JSON
    sample_count INTEGER,
    created_at TEXT
);
```

## REST API

### Tags API

**Create Tag:**
```bash
curl -X POST http://localhost:8080/api/v1/data/tags \
  -H "Content-Type: application/json" \
  -d '{
    "name": "verified",
    "category": "quality",
    "description": "Manually verified data",
    "color": "#4CAF50"
  }'
```

**List Tags:**
```bash
curl http://localhost:8080/api/v1/data/tags?category=quality
```

**Tag a Resource:**
```bash
curl -X POST http://localhost:8080/api/v1/data/tags/assign \
  -H "Content-Type: application/json" \
  -d '{
    "tag_id": "tag-verified",
    "resource_type": "dataset",
    "resource_id": "dataset-001"
  }'
```

### Lineage API

**Record Lineage:**
```bash
curl -X POST http://localhost:8080/api/v1/data/lineage \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model-001",
    "training_job_id": "job-001",
    "dataset_id": "dataset-001",
    "transformation_steps": [...],
    "quality_metrics": {...}
  }'
```

**Get Model Lineage:**
```bash
curl http://localhost:8080/api/v1/data/lineage/model/model-001
```

## Web UI

The Web UI provides visual interfaces for data observability:

### Data Training Page

Navigate to: http://localhost:3000/data/training

Features:
- Dataset browser with tag filtering
- Quality metrics dashboard
- Lineage visualization

### Model Page

Navigate to: http://localhost:3000/models/{model_id}

Shows:
- Training data lineage
- Data quality at training time
- Transformation history

## Best Practices

### Tagging Strategy

1. **Use consistent naming**: lowercase, underscores
2. **Define tag taxonomy upfront**: Agree on categories
3. **Tag at ingestion**: Tag data when first added
4. **Review regularly**: Update tags as understanding improves

### Lineage Recording

1. **Record automatically**: Integrate with training pipeline
2. **Include all transformations**: Don't skip "minor" steps
3. **Store quality metrics**: Capture at each stage
4. **Version datasets**: Enable reproducibility

### Quality Monitoring

1. **Set baselines**: Establish quality thresholds
2. **Alert on issues**: Don't let bad data slip through
3. **Regular audits**: Periodic human review
4. **Track trends**: Monitor quality over time

## Integration with Training

The data observability system integrates automatically with training:

```python
from agentic_assistants.training import TrainingJobManager

manager = TrainingJobManager()
job = manager.create_job(config)

# Lineage is automatically recorded when training completes
# Including:
# - Dataset used
# - Transformations applied
# - Quality metrics
# - Model output
```

## Compliance and Governance

For regulated environments:

### Audit Trail

```python
# Get full history for a dataset
history = tracker.get_audit_trail("dataset-001")

for event in history:
    print(f"{event.timestamp}: {event.action} by {event.user}")
```

### Data Retention

```python
# Set retention policies
from agentic_assistants.data.training.governance import RetentionPolicy

policy = RetentionPolicy(
    resource_type="dataset",
    max_age_days=365,
    archive_action="compress",
)
```

### Access Control

```python
# Tag-based access control
from agentic_assistants.data.training.governance import AccessControl

access = AccessControl()
access.restrict_by_tag(
    tag_id="tag-sensitive",
    allowed_users=["admin", "data-team"],
)
```
