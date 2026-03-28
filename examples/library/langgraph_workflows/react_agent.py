# requires: langgraph
"""LangGraph ReAct agent: reason-act-observe loop.

Demonstrates:
- Agent node that decides to use tools or finish
- Tool node that executes selected tools
- Conditional edge for the agent loop
"""

from __future__ import annotations

import ast
import operator
from typing import Literal

from typing_extensions import TypedDict

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

_KNOWLEDGE_BASE = {
    "meaning of life": "42 (per Douglas Adams, Hitchhiker's Guide).",
    "pi": "3.141592653589793",
    "e": "2.718281828459045",
}


def evaluate_calculator(expression: str) -> float:
    """Safely evaluate a numeric expression using AST (no arbitrary calls)."""
    tree = ast.parse(expression.strip(), mode="eval")

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError("only int/float constants allowed")
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return float(_ALLOWED_UNARY[type(node.op)](_eval(node.operand)))
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            left, right = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("division by zero")
            return float(_ALLOWED_BINOPS[type(node.op)](left, right))
        raise ValueError(f"unsupported expression node: {type(node).__name__}")

    return _eval(tree.body)


def run_calculator_tool(user_input: str) -> str:
    try:
        value = evaluate_calculator(user_input)
        return f"calculator({user_input!r}) = {value}"
    except Exception as exc:
        return f"calculator error for {user_input!r}: {type(exc).__name__}: {exc}"


def run_lookup_tool(user_input: str) -> str:
    key = user_input.lower().strip()
    hit = _KNOWLEDGE_BASE.get(key)
    if hit is None:
        return f"lookup({user_input!r}): no local entry (try keys {list(_KNOWLEDGE_BASE)!r})"
    return f"lookup({user_input!r}): {hit}"


class AgentState(TypedDict, total=False):
    messages: list[dict]
    tool_calls: list[dict]
    tool_results: list[str]
    final_answer: str
    iterations: int
    query: str


def agent_node(state: AgentState) -> dict:
    """Agent decides: use a tool or give final answer based on prior observations."""
    iterations = state.get("iterations", 0)
    tool_results = state.get("tool_results") or []

    if tool_results:
        combined = "; ".join(tool_results)
        return {
            "final_answer": (
                f"Synthesized after tool execution: {combined} "
                f"(agent steps: {iterations + 1})"
            ),
            "iterations": iterations + 1,
        }

    if iterations >= 6:
        return {
            "final_answer": "Stopped: iteration budget exceeded without a resolution path.",
            "iterations": iterations + 1,
        }

    expr = state.get("query") or "(17 + 8) * 4 - 12 / 3"
    if iterations == 0:
        return {
            "tool_calls": [{"tool": "calculator", "input": expr}],
            "iterations": iterations + 1,
        }
    return {
        "tool_calls": [{"tool": "lookup", "input": "meaning of life"}],
        "iterations": iterations + 1,
    }


def tool_node(state: AgentState) -> dict:
    """Execute tool calls and append real computed / lookup results."""
    results: list[str] = []
    for call in state.get("tool_calls", []):
        name = str(call.get("tool", ""))
        arg = call.get("input", "")
        if name == "calculator":
            results.append(run_calculator_tool(str(arg)))
        elif name == "lookup":
            results.append(run_lookup_tool(str(arg)))
        else:
            results.append(f"unknown tool {name!r} (input={arg!r})")
    return {"tool_results": results, "tool_calls": []}


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    if state.get("final_answer"):
        return "end"
    if state.get("tool_calls"):
        return "tools"
    return "end"


def demo_react_agent():
    try:
        from langgraph.graph import END, START, StateGraph

        workflow = StateGraph(AgentState)

        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {"tools": "tools", "end": END},
        )
        workflow.add_edge("tools", "agent")

        graph = workflow.compile()

        result = graph.invoke(
            {
                "messages": [],
                "tool_calls": [],
                "tool_results": [],
                "final_answer": "",
                "iterations": 0,
                "query": "(256 // 4) + 11 * 3",
            }
        )

        print("ReAct agent result:")
        print(f"  Final answer: {result['final_answer']}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Tool results (trace): {result.get('tool_results', [])}")

    except ImportError:
        print("Install: pip install langgraph")


def main() -> None:
    """Entry point: compile the graph and run a ReAct loop with real tool math/lookup."""
    demo_react_agent()


if __name__ == "__main__":
    main()
