# Chunk: fdba26acb888_2

- source: `docs/data_observability.md`
- lines: 215-350
- chunk: 3/5

```
urce
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
```
