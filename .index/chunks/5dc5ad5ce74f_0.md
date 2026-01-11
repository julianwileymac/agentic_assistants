# Chunk: 5dc5ad5ce74f_0

- source: `docs/knowledge_bases.md`
- lines: 1-38
- chunk: 1/1

```
# Knowledge Bases

The `agentic_assistants.knowledge` package provides a unified “knowledge base” abstraction used by agents and tools to:

- store documents
- run semantic search
- (optionally) perform RAG-style query answering

## Types

- **VectorKnowledgeBase**: vector search over stored documents
- **RAGKnowledgeBase**: vector retrieval + generation
- **HybridKnowledgeBase**: combines vector retrieval with structured/contextual data paths

## Basic usage

```python
from agentic_assistants.knowledge import get_knowledge_base

kb = get_knowledge_base("my-project", kb_type="hybrid")

kb.add_documents(
    ["Design doc: ...", "Runbook: ..."],
    metadatas=[{"source": "docs"}, {"source": "ops"}],
)

results = kb.search("runbook", top_k=5)
answer = kb.query("How do we start the server?")
```

## Storage and backends

Vector-backed knowledge bases use the configured vector store backends (LanceDB/Chroma). See:

- `AgenticConfig.vectordb.*`
- `docs/configuration.md`

```
