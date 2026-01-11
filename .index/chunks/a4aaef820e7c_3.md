# Chunk: a4aaef820e7c_3

- source: `notebooks/03_langgraph_basics.ipynb`
- lines: 244-292
- chunk: 4/4

```
,
        "\n",
        "print(\"Streaming execution:\")\n",
        "print(\"-\" * 40)\n",
        "\n",
        "for step_output in adapter.stream_graph(\n",
        "    workflow,\n",
        "    inputs=initial_state,\n",
        "    experiment_name=\"langgraph-streaming\",\n",
        "):\n",
        "    for node_name, node_output in step_output.items():\n",
        "        print(f\"✓ Node: {node_name}\")\n",
        "        if \"steps\" in node_output:\n",
        "            print(f\"  Steps: {node_output['steps']}\")\n"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## What's Being Tracked?\n",
        "\n",
        "The LangGraph adapter provides:\n",
        "\n",
        "**MLFlow:**\n",
        "- Workflow parameters\n",
        "- Total execution duration\n",
        "- Success/failure status\n",
        "- Final state as artifact\n",
        "\n",
        "**OpenTelemetry:**\n",
        "- Span for entire workflow\n",
        "- Child spans for each node\n",
        "- Node execution times\n",
        "- State transitions\n",
        "\n",
        "View traces in Jaeger UI: http://localhost:16686\n"
      ]
    }
  ],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}
```
