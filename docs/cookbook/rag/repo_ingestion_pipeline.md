# Repo Ingestion Pipeline

Use this recipe to continuously ingest repositories into a shared collection.

```bash
python -m agentic_assistants.pipelines.run_repo_ingestion \
  --config examples/global-knowledgebase-starter/config.yaml
```

```python
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline

pipe = create_repo_ingestion_pipeline(
    config_path="examples/global-knowledgebase-starter/config.yaml"
)
```

Pair this with scheduled runs and summary files to monitor drift across upstream repositories.

