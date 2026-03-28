# requires: ragas
"""Agent metrics: tool_call_accuracy, agent goal accuracy, topic_adherence."""

from __future__ import annotations


def main() -> None:
    print("RAGAS agent-oriented metrics with sample traces")
    print("-" * 60)

    sample_traces = [
        {
            "user_input": "Book a table for two at 7pm.",
            "reference_tool_calls": [
                {"name": "search_restaurant", "args": {"city": "NYC"}},
                {"name": "book_table", "args": {"party_size": 2, "time": "19:00"}},
            ],
            "tool_calls": [
                {"name": "search_restaurant", "args": {"city": "NYC"}},
                {"name": "book_table", "args": {"party_size": 2, "time": "19:00"}},
            ],
            "final_output": "Your table for two is booked at 7pm.",
            "reference_final_output": "Your table for two is booked at 7pm.",
            "topics": ["reservation", "restaurant"],
        },
        {
            "user_input": "Summarize the quarterly revenue.",
            "reference_tool_calls": [{"name": "fetch_report", "args": {"id": "Q1"}}],
            "tool_calls": [{"name": "web_search", "args": {"q": "revenue"}}],
            "final_output": "Here is a generic web summary.",
            "reference_final_output": "Q1 revenue was $12M per internal report.",
            "topics": ["finance", "internal_report"],
        },
    ]
    print("Sample agent traces (abbreviated):")
    for t in sample_traces:
        print(f"  user: {t['user_input']!r}")
        print(f"    tools expected: {[x['name'] for x in t['reference_tool_calls']]}")
        print(f"    tools used:     {[x['name'] for x in t['tool_calls']]}")

    try:
        from datasets import Dataset
        from ragas import evaluate
    except ImportError:
        print(
            "Missing ragas/datasets. Install with:\n"
            "  pip install ragas datasets"
        )
        return

    metric_objects = []
    import_errors = []

    for path in (
        ("ragas.metrics", "tool_call_accuracy"),
        ("ragas.metrics", "ToolCallAccuracy"),
        ("ragas.metrics", "topic_adherence"),
        ("ragas.metrics", "TopicAdherence"),
        ("ragas.metrics", "agent_goal_accuracy"),
        ("ragas.metrics", "AgentGoalAccuracyWithReference"),
    ):
        mod, name = path
        try:
            imported = __import__(mod, fromlist=[name])
            obj = getattr(imported, name, None)
            if obj is not None:
                metric_objects.append(obj)
        except (ImportError, AttributeError) as e:
            import_errors.append(f"{mod}.{name}: {e}")

    if not metric_objects:
        print("Could not import agent metrics from ragas.metrics (API differs by version).")
        for line in import_errors[:6]:
            print(" ", line)
        print(
            "\nPrint-only rubric:\n"
            "  - tool_call_accuracy: compare actual vs reference tool names/args.\n"
            "  - agent_goal_accuracy: did the final outcome satisfy the user task?\n"
            "  - topic_adherence: stay on requested topics vs drift.\n"
        )
        return

    # Minimal dataset keys depend on metric; this may still fail without LLM backends.
    ds = Dataset.from_dict(
        {
            "user_input": [t["user_input"] for t in sample_traces],
            "reference_tool_calls": [t["reference_tool_calls"] for t in sample_traces],
            "tool_calls": [t["tool_calls"] for t in sample_traces],
            "response": [t["final_output"] for t in sample_traces],
            "reference": [t["reference_final_output"] for t in sample_traces],
        }
    )
    print(f"\nAttempting evaluate() with metrics: {[getattr(m, '__name__', str(m)) for m in metric_objects]}")
    try:
        out = evaluate(ds, metrics=metric_objects)
        print(out)
    except Exception as exc:
        print(f"evaluate() skipped or failed: {exc}")
        print("Agent metrics often need LLM judges and exact column names for your RAGAS version.")


if __name__ == "__main__":
    main()
