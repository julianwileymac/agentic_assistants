# Chunk: fdba26acb888_0

- source: `docs/data_observability.md`
- lines: 1-118
- chunk: 1/5

```
﻿# Data Observability Guide

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
```
