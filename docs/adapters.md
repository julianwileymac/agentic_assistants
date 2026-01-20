# Agent Framework Adapters

The Agentic Assistants framework provides adapters for multiple agent frameworks, all with integrated observability (MLFlow tracking, OpenTelemetry tracing) and usage analytics.

## Supported Frameworks

| Framework | Adapter | Description |
|-----------|---------|-------------|
| CrewAI | `CrewAIAdapter` | Multi-agent crew orchestration |
| LangGraph | `LangGraphAdapter` | Graph-based workflow orchestration |
| AutoGen | `AutoGenAdapter` | Microsoft multi-agent conversations |
| Google ADK | `GoogleADKAdapter` | Google Agent Development Kit |
| Agno | `AgnoAdapter` | Modern framework with reasoning modes |
| LangFlow | `LangFlowAdapter` | Visual workflow builder |

## Quick Start

```python
from agentic_assistants.adapters import get_adapter

# Get an adapter by framework name
adapter = get_adapter("crewai")

# Or import directly
from agentic_assistants.adapters import CrewAIAdapter, LangGraphAdapter
```

## Common Features

All adapters provide:

- **MLFlow Tracking**: Experiment tracking for runs
- **OpenTelemetry Tracing**: Distributed tracing
- **Usage Tracking**: Analytics for meta-analysis
- **RAG Integration**: Connect knowledge bases
- **Memory Support**: Persistent conversation memory
- **Kubernetes Deployment**: Deploy agents to K8s

### Connecting RAG

```python
from agentic_assistants.knowledge import get_knowledge_base

adapter = CrewAIAdapter()
kb = get_knowledge_base("my_project")
adapter.connect_rag(kb)
```

### Connecting Memory

```python
from agentic_assistants.memory import get_memory_store

memory = get_memory_store(backend="mem0")
adapter.connect_memory(memory)
```

## CrewAI Adapter

```python
from agentic_assistants.adapters import CrewAIAdapter

adapter = CrewAIAdapter()

# Create an agent
agent = adapter.create_ollama_agent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert researcher with attention to detail",
)

# Create a task
task = adapter.create_task(
    description="Research quantum computing",
    agent=agent,
    expected_output="A summary of key concepts",
)

# Create and run a crew
crew = adapter.create_crew(agents=[agent], tasks=[task])
result = adapter.run_crew(
    crew,
    inputs={"topic": "quantum computing"},
    experiment_name="research-experiment"
)
```

## LangGraph Adapter

```python
from agentic_assistants.adapters import LangGraphAdapter
from typing import TypedDict

class MyState(TypedDict):
    messages: list
    current_step: str

adapter = LangGraphAdapter()

# Create a graph
graph = adapter.create_state_graph(MyState)

# Add nodes
def process_node(state):
    return {"current_step": "processed"}

graph.add_node("process", process_node)

# Compile and run
compiled = graph.compile()
result = adapter.run_graph(
    compiled,
    initial_state={"messages": [], "current_step": "start"},
    experiment_name="workflow-experiment"
)
```

## AutoGen Adapter

```python
from agentic_assistants.adapters import AutoGenAdapter

adapter = AutoGenAdapter()

# Create agents
assistant = adapter.create_assistant_agent(
    name="assistant",
    system_message="You are a helpful coding assistant.",
)

user_proxy = adapter.create_user_proxy_agent(
    name="user_proxy",
    human_input_mode="NEVER",
)

# Run conversation
result = adapter.run_conversation(
    user_proxy,
    assistant,
    message="Write a function to calculate fibonacci numbers",
    experiment_name="code-gen"
)

# Group chat
agents = [assistant, adapter.create_assistant_agent("reviewer", "You review code.")]
group_chat = adapter.create_group_chat(agents, max_round=5)
manager = adapter.create_group_chat_manager(group_chat)

result = adapter.run_group_chat(
    user_proxy,
    manager,
    message="Implement and review a sorting algorithm"
)
```

## Google ADK Adapter

```python
from agentic_assistants.adapters import GoogleADKAdapter

adapter = GoogleADKAdapter()

# Create an agent
agent = adapter.create_agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    model="llama3.2",
)

# Run the agent
result = adapter.run_agent(
    agent,
    query="What is machine learning?",
    experiment_name="qa-experiment"
)

# Session management
session_id = adapter.create_session()
adapter.add_to_session(session_id, "user", "Hello!")
adapter.add_to_session(session_id, "assistant", "Hi there!")
```

## Agno Adapter

```python
from agentic_assistants.adapters import AgnoAdapter

adapter = AgnoAdapter()

# Create an agent with reasoning
agent = adapter.create_agent(
    name="researcher",
    instructions="You are a research assistant.",
    reasoning="cot",  # chain-of-thought
)

# Run the agent
result = adapter.run_agent(
    agent,
    query="Explain quantum entanglement",
    reasoning_mode="cot",
    experiment_name="research"
)

# Create a team
agent2 = adapter.create_agent(name="writer", instructions="You write clearly.")
team = adapter.create_team(
    name="research_team",
    agents=[agent, agent2],
    mode="coordinate"
)

result = adapter.run_team(team, query="Write about quantum computing")
```

## LangFlow Adapter

```python
from agentic_assistants.adapters import LangFlowAdapter

adapter = LangFlowAdapter()

# Run a flow from JSON
result = adapter.run_flow(
    flow_definition=flow_json,
    inputs={"query": "Hello!"},
    experiment_name="chat-flow"
)

# Run from file
result = adapter.run_flow_file(
    "path/to/flow.json",
    inputs={"query": "Hello!"}
)

# Create a simple chat flow
flow = adapter.create_simple_chat_flow(
    system_message="You are a helpful assistant.",
    model="llama3.2"
)
result = adapter.run_flow(flow, inputs={"query": "Hi!"})
```

## Kubernetes Deployment

All adapters support Kubernetes deployment:

```python
# Deploy a CrewAI crew
deployment = await adapter.deploy_crew(
    crew_id="my-crew",
    name="research-crew",
    model_endpoint="http://ollama.model-serving:11434",
)

# Deploy a LangGraph flow
deployment = await adapter.deploy_graph(
    flow_id="my-flow",
    name="chat-flow",
    state_backend="minio",
)

# Deploy an AutoGen team
deployment = await adapter.deploy_autogen_team(
    team_id="my-team",
    name="code-team",
    agents_config=[...],
)
```

## Installation

Install optional dependencies for additional frameworks:

```bash
# AutoGen
pip install pyautogen

# Agno
pip install agno

# LangFlow
pip install langflow

# Or install all
pip install agentic-assistants[assistant]
```

## See Also

- [Framework Assistant](framework_assistant.md) - Built-in assistant
- [Ollama Fine-Tuning](ollama_finetuning.md) - Model customization
- [Kubernetes Deployment](kubernetes.md) - Deployment guide
