# Chunk: fdba26acb888_3

- source: `docs/data_observability.md`
- lines: 333-471
- chunk: 4/5

```
ags \
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
```
