# Local Coding Assistant Starter

A comprehensive starter project for building a local agentic coding assistant with RAG, memory persistence, and episodic learning capabilities.

## Overview

This starter implements a coding assistant that:
- Indexes and searches your local codebase
- Maintains persistent memory of conversations and decisions
- Learns from past interactions through episodic memory
- Caches reusable solutions for quick retrieval
- Tracks document lineage for provenance

## Features

- **Multi-level Vector Store**: Project-scoped collections with global knowledge sharing
- **Persistent Memory**: mem0-backed agent memory with semantic search
- **Episodic Learning**: Records conversations, tasks, errors, and learnings
- **Solution Cache**: Redis-backed cache for reusable code patterns
- **Document Lineage**: Full provenance tracking for knowledge base documents

## Quick Start

### 1. Install Dependencies

```bash
pip install agentic-assistants[coding-assistant]
# Or with all optional dependencies:
pip install agentic-assistants[all]
```

### 2. Configure the Assistant

Copy and customize the config file:

```bash
cp examples/local-coding-assistant/config.yaml my-assistant-config.yaml
```

Edit `my-assistant-config.yaml`:
- Set your project paths
- Configure embedding model (local Ollama or remote)
- Adjust memory and cache settings

### 3. Index Your Codebase

```bash
python -m examples.local-coding-assistant.index_codebase --path /path/to/your/code --config my-assistant-config.yaml
```

### 4. Run the Assistant

```python
from examples.local_coding_assistant import CodingAssistant

assistant = CodingAssistant(config_path="my-assistant-config.yaml")

# Ask questions about your codebase
response = assistant.ask("How does the authentication module work?")
print(response)

# The assistant remembers context
response = assistant.ask("Can you show me the related tests?")
print(response)
```

## Project Structure

```
local-coding-assistant/
├── README.md              # This file
├── config.yaml            # Configuration template
├── __init__.py            # Package init
├── agents/                # Agent definitions
│   ├── __init__.py
│   ├── coding_agent.py    # Main coding assistant agent
│   ├── researcher.py      # Research and analysis agent
│   └── reviewer.py        # Code review agent
├── tools/                 # Custom tools
│   ├── __init__.py
│   ├── code_search.py     # Codebase search tools
│   ├── file_ops.py        # File operation tools
│   └── analysis.py        # Code analysis tools
├── workflows/             # Multi-agent workflows
│   ├── __init__.py
│   ├── code_review.py     # Code review workflow
│   └── documentation.py   # Documentation generation
└── index_codebase.py      # Codebase indexing script
```

## Configuration

### Vector Store

```yaml
vectordb:
  backend: lancedb  # or chromadb
  default_scope: project
  project_path_template: "data/vectordb/{project_id}"
  enable_cross_scope_search: true
```

### Memory

```yaml
memory:
  backend: mem0
  embedding_model: nomic-embed-text
  persistence_path: data/memory
  context_window: 10
```

### Cache

```yaml
cache:
  enabled: true
  url: redis://localhost:6379
  solution_ttl_hours: 168  # 1 week
```

### Embeddings

```yaml
embedding:
  mode: local  # or remote
  local_provider: ollama
  local_model: nomic-embed-text
  # For remote:
  # remote_provider: openai
  # openai_api_key: ${OPENAI_API_KEY}
```

## Usage Examples

### Basic Q&A

```python
from examples.local_coding_assistant import CodingAssistant

assistant = CodingAssistant()

# Simple question
response = assistant.ask("What does the UserService class do?")

# Follow-up with context
response = assistant.ask("Show me how it handles authentication")
```

### Code Review

```python
from examples.local_coding_assistant.workflows import CodeReviewWorkflow

workflow = CodeReviewWorkflow()
review = workflow.review_file("src/services/user.py")

print(review.summary)
print(review.suggestions)
```

### Documentation Generation

```python
from examples.local_coding_assistant.workflows import DocumentationWorkflow

workflow = DocumentationWorkflow()
docs = workflow.generate_module_docs("src/services/")

# Write to files
docs.save("docs/api/")
```

### Research Mode

```python
from examples.local_coding_assistant.agents import ResearchAgent

researcher = ResearchAgent()

# Deep dive into a topic
report = researcher.investigate("How does the caching layer work?")
print(report.findings)
print(report.recommendations)
```

## Memory and Learning

### View Past Interactions

```python
# Get recent conversation history
history = assistant.memory.get_recent_episodes(limit=10)

# Search past learnings
learnings = assistant.memory.get_learnings(topic="authentication")
```

### Manual Memory Addition

```python
# Add a learning
assistant.memory.record_learning(
    learning="The auth module uses JWT tokens with 1-hour expiry",
    context={"module": "auth", "file": "auth/jwt.py"}
)
```

### Solution Caching

```python
# Store a reusable solution
assistant.cache.store_solution(
    name="jwt-validation",
    description="Standard JWT token validation pattern",
    code='''
def validate_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    ''',
    tags=["auth", "jwt", "validation"]
)

# Retrieve later
solution = assistant.cache.get_solution("jwt-validation")
```

## API Integration

### REST API

The assistant exposes a REST API when running in server mode:

```bash
python -m examples.local_coding_assistant.server --config my-config.yaml
```

Endpoints:
- `POST /api/assistant/ask` - Ask a question
- `GET /api/assistant/memory` - Get memory stats
- `POST /api/assistant/index` - Index new files

### MCP Integration

Use with Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "coding-assistant": {
      "command": "python",
      "args": ["-m", "examples.local_coding_assistant.mcp_server"],
      "env": {
        "ASSISTANT_CONFIG": "/path/to/my-config.yaml"
      }
    }
  }
}
```

## Advanced Features

### Custom Tools

Add your own tools:

```python
from agentic_assistants.agents import tool

@tool(description="Run unit tests for a module")
def run_tests(module_path: str) -> str:
    import subprocess
    result = subprocess.run(
        ["pytest", module_path, "-v"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Multi-Agent Workflows

Create complex workflows with multiple agents:

```python
from examples.local_coding_assistant.agents import (
    CodingAgent,
    ResearchAgent,
    ReviewerAgent,
)
from agentic_assistants.workflows import Workflow

workflow = Workflow([
    ("research", ResearchAgent(), "Analyze the problem"),
    ("implement", CodingAgent(), "Write the solution"),
    ("review", ReviewerAgent(), "Review the code"),
])

result = workflow.run("Add rate limiting to the API endpoints")
```

## Troubleshooting

### Memory Issues

If mem0 fails to initialize:
```bash
# Ensure Ollama is running with embedding model
ollama pull nomic-embed-text
```

### Redis Connection

If cache is unavailable:
```bash
# Start Redis locally
docker run -d -p 6379:6379 redis:alpine
```

### Indexing Large Codebases

For large repositories, use incremental indexing:
```python
assistant.index_incremental(
    path="/path/to/code",
    file_types=[".py", ".ts", ".js"],
    max_workers=4
)
```

## Contributing

See the main project's contributing guidelines. For this starter specifically:

1. Keep agents focused on single responsibilities
2. Document all tool parameters
3. Add tests for new workflows
4. Update this README for new features

## License

Same as the main agentic-assistants project.
