# Chunk: fdba26acb888_4

- source: `docs/data_observability.md`
- lines: 453-481
- chunk: 5/5

```
event.action} by {event.user}")
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
```
