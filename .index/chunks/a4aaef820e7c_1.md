# Chunk: a4aaef820e7c_1

- source: `notebooks/03_langgraph_basics.ipynb`
- lines: 77-171
- chunk: 2/4

```
# Tracks completed steps\n",
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
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# Create LLM instance\n",
        "llm = adapter.create_ollama_llm()\n",
        "\n",
        "def analyze_question(state: QAState) -> QAState:\n",
        "    \"\"\"Analyze the question to generate context.\"\"\"\n",
        "    question = state[\"question\"]\n",
        "    \n",
        "    prompt = f\"\"\"Analyze this question and provide relevant context:\n",
        "    \n",
        "Question: {question}\n",
        "\n",
        "Provide:\n",
        "1. Key concepts involved\n",
        "2. What information is needed to answer\n",
        "3. Any assumptions to consider\"\"\"\n",
        "    \n",
        "    response = llm.invoke(prompt)\n",
        "    \n",
        "    return {\n",
        "        \"context\": response.content,\n",
        "        \"steps\": [\"question_analyzed\"],\n",
        "    }\n",
        "\n",
        "def generate_answer(state: QAState) -> QAState:\n",
        "    \"\"\"Generate an answer based on context.\"\"\"\n",
        "    question = state[\"question\"]\n",
        "    context = state[\"context\"]\n",
        "    \n",
        "    prompt = f\"\"\"Based on this analysis, provide a clear answer.\n",
        "\n",
        "Question: {question}\n",
        "\n",
        "Context/Analysis: {context}\n",
        "\n",
        "Provide a direct, helpful answer.\"\"\"\n",
        "    \n",
        "    response = llm.invoke(prompt)\n",
        "    \n",
        "    return {\n",
        "        \"answer\": response.content,\n",
        "        \"confidence\": 0.8,  # Could be computed based on response\n",
        "        \"steps\": [\"answer_generated\"],\n",
        "    }\n",
        "\n",
        "def format_response(state: QAState) -> QAState:\n",
        "    \"\"\"Format the final response.\"\"\"\n",
        "    answer = state[\"answer\"]\n",
        "    confidence = state[\"confidence\"]\n",
        "    \n",
        "    formatted = f\"📝 Answer:\\n\\n{answer}\\n\\n(Confidence: {confidence:.0%})\"\n",
        "    \n",
        "    return {\n",
        "        \"answer\": formatted,\n",
        "        \"steps\": [\"response_formatted\"],\n",
        "    }\n",
        "\n",
        "print(\"Node functions defined!\")\n"
      ]
    },
    {
      "cell_type": "markdown",
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
```
