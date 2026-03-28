# requires: langgraph langchain-core
"""LangGraph basic StateGraph with TypedDict state.

Demonstrates:
- StateGraph definition with TypedDict
- add_node, add_edge, add_conditional_edges
- START/END constants
- Compile and invoke
"""

from __future__ import annotations

from typing import Literal
from typing_extensions import TypedDict


class ConversationState(TypedDict):
    messages: list[str]
    current_speaker: str
    turn_count: int
    is_complete: bool


def greeter(state: ConversationState) -> dict:
    return {
        "messages": state["messages"] + [f"Hello from greeter! Turn {state['turn_count']}"],
        "turn_count": state["turn_count"] + 1,
    }


def responder(state: ConversationState) -> dict:
    return {
        "messages": state["messages"] + [f"Response from responder! Turn {state['turn_count']}"],
        "turn_count": state["turn_count"] + 1,
    }


def should_continue(state: ConversationState) -> Literal["continue", "end"]:
    if state["turn_count"] >= 4:
        return "end"
    return "continue"


def demo_basic_state_graph():
    """Build and run a basic LangGraph StateGraph."""
    try:
        from langgraph.graph import StateGraph, START, END

        workflow = StateGraph(ConversationState)

        workflow.add_node("greeter", greeter)
        workflow.add_node("responder", responder)

        workflow.add_edge(START, "greeter")
        workflow.add_edge("greeter", "responder")
        workflow.add_conditional_edges(
            "responder",
            should_continue,
            {"continue": "greeter", "end": END},
        )

        graph = workflow.compile()

        initial_state: ConversationState = {
            "messages": [],
            "current_speaker": "greeter",
            "turn_count": 0,
            "is_complete": False,
        }

        result = graph.invoke(initial_state)
        print("Final state:")
        print(f"  Messages: {result['messages']}")
        print(f"  Turns: {result['turn_count']}")

    except ImportError:
        print("Install: pip install langgraph langchain-core")


if __name__ == "__main__":
    demo_basic_state_graph()
