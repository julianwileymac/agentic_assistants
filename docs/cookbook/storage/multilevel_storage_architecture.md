# Multi-Level Storage Architecture

Use this architecture for durable local systems:

1. file artifacts for raw and transformed chunks
2. vector store for semantic retrieval
3. SQLite for operational usage events

```text
data/
  artifacts/
  vectors/
  usage.db
  traces/
```

This separation keeps retrieval fast while preserving an auditable processing history.

