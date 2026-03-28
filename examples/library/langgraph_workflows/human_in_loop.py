# requires: langgraph langchain-core
"""LangGraph human-in-the-loop with interrupt_before.

Demonstrates:
- Interrupt graph execution for human approval
- Resume after human input
- Approval gate pattern
"""

from __future__ import annotations

from typing import Literal
from typing_extensions import TypedDict


class ApprovalState(TypedDict):
    proposal: str
    approved: bool
    feedback: str
    result: str


def generate_proposal(state: ApprovalState) -> dict:
    return {"proposal": "Deploy v2.0 to production with rolling update strategy"}


def execute_action(state: ApprovalState) -> dict:
    if state.get("approved"):
        return {"result": f"Executed: {state['proposal']}"}
    return {"result": f"Rejected: {state.get('feedback', 'No feedback')}"}


def check_approval(state: ApprovalState) -> Literal["execute", "rejected"]:
    if state.get("approved"):
        return "execute"
    return "rejected"


def demo_human_in_loop():
    """Show interrupt_before for human approval gates."""
    try:
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import MemorySaver

        memory = MemorySaver()

        workflow = StateGraph(ApprovalState)
        workflow.add_node("propose", generate_proposal)
        workflow.add_node("execute", execute_action)

        workflow.add_edge(START, "propose")
        workflow.add_conditional_edges(
            "propose",
            check_approval,
            {"execute": "execute", "rejected": END},
        )
        workflow.add_edge("execute", END)

        graph = workflow.compile(
            checkpointer=memory,
            interrupt_before=["execute"],
        )

        config = {"configurable": {"thread_id": "approval-001"}}

        print("Phase 1: Generate proposal (will interrupt before execute)")
        result = graph.invoke(
            {"proposal": "", "approved": True, "feedback": "", "result": ""},
            config=config,
        )
        print(f"  Proposal: {result.get('proposal', 'pending')}")
        print(f"  (Graph interrupted - awaiting human approval)")
        print()
        print("In production, the human reviews and resumes:")
        print("  graph.invoke({'approved': True}, config=config)")

    except ImportError:
        print("Install: pip install langgraph langchain-core")


if __name__ == "__main__":
    demo_human_in_loop()
