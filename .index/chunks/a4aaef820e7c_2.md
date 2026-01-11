# Chunk: a4aaef820e7c_2

- source: `notebooks/03_langgraph_basics.ipynb`
- lines: 157-254
- chunk: 3/4

```
e": "markdown",
      "metadata": {},
      "source": [
        "## Building the Graph\n",
        "\n",
        "Now we assemble the nodes into a workflow:\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "from langgraph.graph import StateGraph, END\n",
        "\n",
        "# Create the graph\n",
        "graph = adapter.create_state_graph(QAState)\n",
        "\n",
        "# Add nodes (wrapped for tracing)\n",
        "graph.add_node(\"analyze\", adapter.wrap_node(analyze_question, \"analyze\"))\n",
        "graph.add_node(\"answer\", adapter.wrap_node(generate_answer, \"answer\"))\n",
        "graph.add_node(\"format\", adapter.wrap_node(format_response, \"format\"))\n",
        "\n",
        "# Define the flow\n",
        "graph.set_entry_point(\"analyze\")\n",
        "graph.add_edge(\"analyze\", \"answer\")\n",
        "graph.add_edge(\"answer\", \"format\")\n",
        "graph.add_edge(\"format\", END)\n",
        "\n",
        "# Compile the graph\n",
        "workflow = graph.compile()\n",
        "print(\"Workflow compiled!\")\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Running the Workflow\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Initial state\n",
        "initial_state: QAState = {\n",
        "    \"question\": \"What are the benefits of using LangGraph for building AI agents?\",\n",
        "    \"context\": \"\",\n",
        "    \"answer\": \"\",\n",
        "    \"confidence\": 0.0,\n",
        "    \"steps\": [],\n",
        "}\n",
        "\n",
        "# Run with tracking\n",
        "result = adapter.run_graph(\n",
        "    workflow,\n",
        "    inputs=initial_state,\n",
        "    experiment_name=\"langgraph-notebook\",\n",
        "    run_name=\"qa-workflow-demo\",\n",
        ")\n",
        "\n",
        "print(\"Steps completed:\", result[\"steps\"])\n",
        "print(\"\\n\" + \"=\"*60)\n",
        "print(result[\"answer\"])\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Streaming Execution\n",
        "\n",
        "You can also stream results as they're generated:\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Streaming example\n",
        "initial_state[\"question\"] = \"How does observability help in AI development?\"\n",
        "initial_state[\"steps\"] = []\n",
        "\n",
        "print(\"Streaming execution:\")\n",
        "print(\"-\" * 40)\n",
        "\n",
        "for step_output in adapter.stream_graph(\n",
        "    workflow,\n",
        "    inputs=initial_state,\n",
        "    experiment_name=\"langgraph-streaming\",\n",
        "):\n",
```
