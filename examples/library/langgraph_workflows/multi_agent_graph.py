# requires: langgraph langchain-core
"""LangGraph multi-agent collaboration via shared state.

Demonstrates:
- Multiple specialized agent nodes
- Shared state that accumulates contributions
- Sequential multi-agent pipeline
"""

from __future__ import annotations

import re
from typing_extensions import TypedDict


class TeamState(TypedDict):
    task: str
    research_notes: list[str]
    code_snippets: list[str]
    review_comments: list[str]
    final_output: str


def _tokenize_task(task: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", task)


def researcher(state: TeamState) -> dict:
    """Derive research notes from the task string (length, vocabulary, heuristics)."""
    task = state["task"].strip()
    tokens = _tokenize_task(task)
    unique = sorted(set(tokens), key=str.lower)
    word_count = len(task.split())
    char_count = len(task)
    top_terms = unique[:6]
    density = (len(unique) / word_count) if word_count else 0.0
    notes = [
        f"Vocabulary: {len(unique)} distinct tokens over {word_count} words "
        f"(lexical density ~{density:.2f}).",
        f"Highlighted terms: {', '.join(top_terms) if top_terms else '(none extracted)'}",
        (
            "Scope heuristic: "
            + (
                "broad - consider staged milestones"
                if word_count > 12
                else "focused - single-sprint prototype viable"
            )
        ),
        f"Character budget: {char_count} chars; average token length "
        f"{char_count / max(word_count, 1):.1f}.",
    ]
    return {"research_notes": notes}


def coder(state: TeamState) -> dict:
    """Build a small Python-shaped artifact from research notes (real string ops)."""
    task = state["task"]
    notes = state.get("research_notes", [])
    slug = re.sub(r"[^a-z0-9]+", "_", task.lower())[:32].strip("_") or "task"
    comment_lines = [f"    # {n}" for n in notes[:3]]
    lines = (
        [
            "from __future__ import annotations",
            "",
            f"def build_{slug}() -> dict[str, object]:",
            '    """Auto scaffold from research summary."""',
        ]
        + comment_lines
        + [
            "    return {",
            '        "pipeline": ["ingest", "transform", "evaluate"],',
            f'        "research_lines": {len(notes)},',
            "    }",
        ]
    )
    return {"code_snippets": lines}


def reviewer(state: TeamState) -> dict:
    """Static checks on generated code lines; produces actionable review comments."""
    code = state.get("code_snippets", [])
    text = "\n".join(code)
    comments: list[str] = []

    if "def " not in text:
        comments.append("Missing a top-level function definition.")
    if "->" not in text:
        comments.append("Add explicit return type hints for public entry points.")
    if text.count('"""') < 2:
        comments.append("Docstring should wrap the function purpose.")
    long_lines = [i for i, line in enumerate(code, 1) if len(line) > 88]
    if long_lines:
        comments.append(f"Lines exceed 88 chars at rows: {long_lines[:5]}")

    if "evaluate" not in text:
        comments.append("Pipeline should include an explicit evaluation stage.")

    risk = "low" if len(comments) <= 1 else "medium"
    final = (
        f"Review outcome ({risk} risk): {len(comments)} finding(s). "
        + ("; ".join(comments) if comments else "No issues flagged by heuristics.")
    )
    return {"review_comments": comments, "final_output": final}


def demo_multi_agent():
    try:
        from langgraph.graph import END, START, StateGraph

        workflow = StateGraph(TeamState)
        workflow.add_node("researcher", researcher)
        workflow.add_node("coder", coder)
        workflow.add_node("reviewer", reviewer)

        workflow.add_edge(START, "researcher")
        workflow.add_edge("researcher", "coder")
        workflow.add_edge("coder", "reviewer")
        workflow.add_edge("reviewer", END)

        graph = workflow.compile()

        result = graph.invoke(
            {
                "task": "Build a sentiment analysis pipeline",
                "research_notes": [],
                "code_snippets": [],
                "review_comments": [],
                "final_output": "",
            }
        )

        print("Multi-agent collaboration result:")
        print("  Research notes:")
        for n in result["research_notes"]:
            print(f"    - {n}")
        print("  Generated code:")
        for line in result["code_snippets"]:
            print(f"    {line}")
        print(f"  Review comments: {result['review_comments']}")
        print(f"  Final: {result['final_output']}")

    except ImportError:
        print("Install: pip install langgraph langchain-core")


def main() -> None:
    """Entry point: run researcher → coder → reviewer on shared state."""
    demo_multi_agent()


if __name__ == "__main__":
    main()
