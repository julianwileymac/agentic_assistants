# Framework Assistant

The Framework Assistant is the built-in AI assistant for Agentic Assistants. It provides comprehensive help with coding, framework guidance, and self-improvement analysis.

## Overview

The Framework Assistant combines three specialized modules:

1. **Coding Helper** - Code generation, review, debugging, and refactoring
2. **Framework Guide** - Help with framework features, configuration, and deployment
3. **Meta Analyzer** - Usage analysis and improvement suggestions

## Quick Start

```python
from agentic_assistants.agents import FrameworkAssistantAgent, create_framework_assistant

# Create with default configuration
assistant = create_framework_assistant()

# Chat with the assistant
response = assistant.chat("How do I create a CrewAI agent?")
print(response)

# Generate code
code = assistant.generate_code("Create a data validation function")
print(code)

# Get improvement suggestions
suggestions = assistant.get_improvement_suggestions()
for s in suggestions:
    print(f"[{s['priority']}] {s['title']}")
```

## Configuration

Configure the assistant in your `.env` file or environment:

```bash
# Enable/disable the assistant
ASSISTANT_ENABLED=true

# Default agent framework
ASSISTANT_DEFAULT_FRAMEWORK=crewai

# LLM model to use
ASSISTANT_MODEL=llama3.2

# Feature toggles
ASSISTANT_ENABLE_CODING_HELPER=true
ASSISTANT_ENABLE_FRAMEWORK_GUIDE=true
ASSISTANT_ENABLE_META_ANALYSIS=true

# RAG and memory
ASSISTANT_RAG_ENABLED=true
ASSISTANT_MEMORY_ENABLED=true

# Usage tracking
ASSISTANT_USAGE_TRACKING_ENABLED=true
```

### Provider-aware assistant configuration

The assistant now supports hybrid provider routing:

```bash
# Assistant-level defaults
ASSISTANT_PROVIDER=ollama
ASSISTANT_MODEL=llama3.2
# ASSISTANT_ENDPOINT=http://localhost:11434

# Optional OpenAI-compatible auth indirection
ASSISTANT_OPENAI_API_KEY_ENV=OPENAI_API_KEY

# HF local/remote mode selection
ASSISTANT_HF_EXECUTION_MODE=hybrid
```

Available provider values:

- `ollama`: local Ollama API (`/api/chat`)
- `huggingface_local`: in-process `transformers` inference
- `openai_compatible`: vLLM/TGI/OpenAI-style chat endpoints

Or configure programmatically:

```python
from agentic_assistants.config import AgenticConfig

config = AgenticConfig()

# Access assistant settings
print(config.assistant.model)
print(config.assistant.enable_coding_helper)
```

## Context options (Control Panel)

The Control Panel chat UI supports optional context injection:

- **Code context**: Loads `.index/context` packs via `ContextLoader` (task-specific when selected).
- **Project docs**: Injects curated excerpts from `docs/` to ground responses.

These are toggles in the assistant chat UI and are sent as `include_code_context`, `include_project_docs`, and `context_task`.

## Features

### Coding Helper

The coding helper provides:

- **Code Generation**: Generate code from natural language descriptions
- **Code Review**: Analyze code for bugs, performance, and best practices
- **Debugging**: Help identify and fix bugs
- **Refactoring**: Suggest improvements and refactorings
- **Code Explanation**: Explain what code does

```python
# Generate code
code = assistant.generate_code(
    "Create a function to validate email addresses",
    language="python"
)

# Review code
review = assistant.review_code("""
def add(a, b):
    return a + b
""")

# Debug code
debug = assistant.debug_code(
    code="...",
    error_message="TypeError: unsupported operand type(s)"
)
```

### Framework Guide

The framework guide helps with:

- **Feature Documentation**: Learn about framework features
- **Configuration Help**: Get help with configuration
- **Deployment Guidance**: Deploy agents and flows
- **Troubleshooting**: Resolve issues

```python
# Get help
help_text = assistant.get_help("How do I use LangGraph?")

# Get configuration help
config_help = assistant.get_configuration_help("kubernetes")

# Get deployment guide
deploy_guide = assistant.get_deployment_guide("agent", target="kubernetes")
```

### Meta Analysis

The meta analyzer provides:

- **Usage Analytics**: Track framework usage
- **Health Score**: Overall framework health assessment
- **Improvement Suggestions**: AI-generated recommendations
- **Trend Analysis**: Usage and error trends

```python
# Get health summary
health = assistant.get_health_summary()
print(f"Health Score: {health['health_score']}")

# Get suggestions
suggestions = assistant.get_improvement_suggestions()

# Generate improvement plan
plan = assistant.generate_improvement_plan()
```

## RAG Integration

Connect knowledge bases for context-aware responses:

```python
from agentic_assistants.knowledge import get_knowledge_base

# Connect code knowledge base
code_kb = get_knowledge_base("my_project")
assistant.connect_code_kb(code_kb)

# Connect docs knowledge base
docs_kb = get_knowledge_base("framework_docs")
assistant.connect_docs_kb(docs_kb)
```

## Memory

Enable persistent memory for conversation continuity:

```python
from agentic_assistants.memory import get_memory_store

memory = get_memory_store(backend="mem0")
assistant.connect_memory(memory)
```

## API Endpoints

The assistant exposes REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assistant/chat` | POST | Chat with the assistant |
| `/api/v1/assistant/config` | GET/PUT | Get/update configuration |
| `/api/v1/assistant/models/catalog` | GET | Unified model picker catalog (Ollama + custom + HF cache) |
| `/api/v1/assistant/analytics` | GET | Get usage analytics |
| `/api/v1/assistant/health` | GET | Get health summary |
| `/api/v1/assistant/suggestions` | GET | Get improvement suggestions |
| `/api/v1/assistant/analyze` | POST | Run meta-analysis |

### Chat API Example

```bash
curl -X POST http://localhost:8080/api/v1/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "How do I create an agent?"}],
    "provider": "openai_compatible",
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "endpoint": "http://localhost:8000/v1"
  }'
```

## WebUI

Access the assistant configuration and analytics through the WebUI:

- **Configuration**: `/assistant` - Configure assistant settings
- **Analytics**: `/assistant/analytics` - View usage analytics and suggestions

## Architecture

```
FrameworkAssistantAgent
├── CodingHelperModule
│   ├── Code Generation
│   ├── Code Review
│   ├── Debugging
│   └── Refactoring
├── FrameworkGuideModule
│   ├── Documentation
│   ├── Configuration Help
│   └── Troubleshooting
└── MetaAnalyzerModule
    ├── Usage Analytics
    ├── Health Assessment
    └── Improvement Suggestions
```

## Best Practices

1. **Enable RAG** for better context-aware responses
2. **Track Usage** to get improvement suggestions
3. **Review Suggestions** regularly to improve framework usage
4. **Use the Right Module** - coding helper for code, guide for framework help

## See Also

- [Adapters](adapters.md) - Framework adapter documentation
- [Ollama Fine-Tuning](ollama_finetuning.md) - Model import and fine-tuning
- [Usage Analytics](usage_analytics.md) - Detailed analytics documentation
