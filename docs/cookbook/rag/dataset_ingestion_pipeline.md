# Dataset Ingestion Pipeline

Use this pattern to convert structured rows into retrieval-ready chunks.

```python
from agentic_assistants.pipelines.templates import create_dataset_ingestion_pipeline

pipe = create_dataset_ingestion_pipeline(
    source_type="file",
    source_config={"filepath": "./data/faq.csv"},
    collection="faq",
    text_column="answer",
)
out = pipe.run()
print(out.success)
```

Prefer explicit `text_column` mappings to avoid noisy concatenation from unrelated columns.

