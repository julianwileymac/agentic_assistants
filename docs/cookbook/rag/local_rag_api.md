# Local RAG API

Use this pattern when you need a service boundary between ingestion and query clients.

```bash
agentic server start --host 127.0.0.1 --port 8080
```

```bash
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Where is context loading implemented?\",\"collection\":\"codebase\",\"top_k\":5}"
```

Keep ingestion and API storage paths aligned so the server reads the same vector collections your pipelines write.

