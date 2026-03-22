# Web Ingestion Pipeline

Use this recipe for periodic ingestion of public web content into local vectors.

```python
from agentic_assistants.pipelines.templates import create_web_ingestion_pipeline

pipeline = create_web_ingestion_pipeline(
    urls=["https://example.com/docs"],
    collection="web_docs",
    chunking_strategy="markdown",
)
result = pipeline.run()
print(result.success)
```

Store source URLs in metadata so you can cite provenance in final answers.

