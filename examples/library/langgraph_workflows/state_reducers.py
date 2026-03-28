# requires: langgraph langchain-core
"""LangGraph custom state reducers for different merge strategies.

Demonstrates:
- Messages that append (list accumulation)
- Counters that increment
- Results that replace
- Using Annotated with operator.add as a reducer
"""

from __future__ import annotations

import operator
from typing import Annotated

from typing_extensions import TypedDict


class ReducerState(TypedDict):
    messages: Annotated[list[str], operator.add]
    counter: Annotated[int, operator.add]
    latest_result: str


def node_a(state: ReducerState) -> dict:
    """Appends to messages, increments counter, sets latest_result."""
    return {
        "messages": ["Node A executed"],
        "counter": 1,
        "latest_result": "result_from_A",
    }


def node_b(state: ReducerState) -> dict:
    return {
        "messages": ["Node B executed"],
        "counter": 1,
        "latest_result": "result_from_B",
    }


def node_c(state: ReducerState) -> dict:
    return {
        "messages": [f"Node C: counter={state['counter']}, last={state['latest_result']}"],
        "counter": 1,
        "latest_result": "result_from_C",
    }


def demo_state_reducers():
    try:
        from langgraph.graph import StateGraph, START, END

        workflow = StateGraph(ReducerState)
        workflow.add_node("a", node_a)
        workflow.add_node("b", node_b)
        workflow.add_node("c", node_c)

        workflow.add_edge(START, "a")
        workflow.add_edge("a", "b")
        workflow.add_edge("b", "c")
        workflow.add_edge("c", END)

        graph = workflow.compile()

        result = graph.invoke({
            "messages": [],
            "counter": 0,
            "latest_result": "",
        })

        print("State reducers demo:")
        print(f"  messages (append): {result['messages']}")
        print(f"  counter (add): {result['counter']}")
        print(f"  latest_result (replace): {result['latest_result']}")

    except ImportError:
        print("Install: pip install langgraph langchain-core")


if __name__ == "__main__":
    demo_state_reducers()
