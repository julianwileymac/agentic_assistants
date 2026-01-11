# Chunk: a4aaef820e7c_0

- source: `notebooks/03_langgraph_basics.ipynb`
- lines: 1-92
- chunk: 1/4

```
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# LangGraph Basics with Agentic Assistants\n",
        "\n",
        "This notebook explores LangGraph integration with the Agentic Assistants framework.\n",
        "\n",
        "## What is LangGraph?\n",
        "\n",
        "LangGraph is a library for building stateful, multi-actor applications with LLMs. Key concepts:\n",
        "- **State**: A shared data structure that flows through the graph\n",
        "- **Nodes**: Functions that process and transform state\n",
        "- **Edges**: Connections that define the flow between nodes\n",
        "- **Conditionals**: Decision points that route to different nodes\n",
        "\n",
        "## Topics Covered\n",
        "\n",
        "1. Understanding state graphs\n",
        "2. Creating nodes with Ollama\n",
        "3. Building workflows\n",
        "4. Running with observability\n",
        "5. Streaming results\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Setup\n",
        "from typing import TypedDict, Annotated, Sequence\n",
        "from operator import add\n",
        "\n",
        "from agentic_assistants import AgenticConfig, OllamaManager\n",
        "from agentic_assistants.adapters import LangGraphAdapter\n",
        "from agentic_assistants.utils.logging import setup_logging\n",
        "\n",
        "setup_logging(level=\"INFO\")\n",
        "\n",
        "# Initialize\n",
        "config = AgenticConfig()\n",
        "ollama = OllamaManager(config)\n",
        "adapter = LangGraphAdapter(config)\n",
        "\n",
        "# Ensure Ollama is ready  \n",
        "ollama.ensure_running()\n",
        "model = ollama.ensure_model()\n",
        "print(f\"Using model: {model}\")\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Defining State\n",
        "\n",
        "State is a TypedDict that flows through your graph:\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Define our workflow state\n",
        "class QAState(TypedDict):\n",
        "    \"\"\"State for a question-answering workflow.\"\"\"\n",
        "    question: str           # The user's question\n",
        "    context: str            # Retrieved or generated context\n",
        "    answer: str             # The final answer\n",
        "    confidence: float       # Confidence score\n",
        "    steps: Annotated[Sequence[str], add]  # Tracks completed steps\n",
        "\n",
        "print(\"State schema defined!\")\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Creating Nodes\n",
        "\n",
        "Nodes are functions that transform state:\n"
      ]
    },
    {
```
