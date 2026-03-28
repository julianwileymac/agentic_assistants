# requires: langgraph langchain-core
"""LangGraph graph with checkpointing for state persistence.

Demonstrates:
- MemorySaver for in-memory checkpointing
- Saving and resuming graph state across sessions
- Thread-based state isolation
"""

from __future__ import annotations

from typing_extensions import TypedDict


class ChatState(TypedDict):
    messages: list[str]
    context: str
    turn: int


def chat_node(state: ChatState) -> dict:
    turn = state.get("turn", 0) + 1
    new_msg = f"[Turn {turn}] Bot response based on context: {state.get('context', 'none')}"
    return {
        "messages": state.get("messages", []) + [new_msg],
        "turn": turn,
    }


def demo_persistent_graph():
    try:
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import MemorySaver

        memory = MemorySaver()

        workflow = StateGraph(ChatState)
        workflow.add_node("chat", chat_node)
        workflow.add_edge(START, "chat")
        workflow.add_edge("chat", END)

        graph = workflow.compile(checkpointer=memory)

        config_thread1 = {"configurable": {"thread_id": "session-001"}}

        result1 = graph.invoke(
            {"messages": ["Hello!"], "context": "greeting", "turn": 0},
            config=config_thread1,
        )
        print(f"Session 1, invoke 1: {result1['messages']}")

        result2 = graph.invoke(
            {"messages": result1["messages"] + ["How are you?"], "context": "follow-up", "turn": result1["turn"]},
            config=config_thread1,
        )
        print(f"Session 1, invoke 2: {result2['messages']}")
        print(f"  Total turns: {result2['turn']}")

    except ImportError:
        print("Install: pip install langgraph langchain-core")


if __name__ == "__main__":
    demo_persistent_graph()
