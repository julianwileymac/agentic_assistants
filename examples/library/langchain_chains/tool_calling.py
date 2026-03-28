# requires: langchain langchain-core
"""Tools: @tool decorator, ToolMessage, binding and manual invocation (stub LLM).

Demonstrates structured args and returning ToolMessage back into a message list.
"""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        from langchain_core.language_models.fake import FakeListChatModel
        from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
        from langchain_core.tools import tool
    except ImportError:
        print("Install: pip install langchain langchain-core")
        return

    @tool
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    @tool
    def weather_city(city: str, unit: str = "celsius") -> dict[str, Any]:
        """Return synthetic weather (structured tool output)."""
        return {"city": city, "temp": 22 if unit == "celsius" else 72, "unit": unit}

    tools = [add, weather_city]
    tool_map = {t.name: t for t in tools}

    print("=== Tool schemas (model-facing) ===")
    for t in tools:
        print(t.name, "->", t.args_schema.model_json_schema() if t.args_schema else "n/a")

    # Bind tools to a chat model (FakeListChatModel may not emit real tool_calls; show manual flow)
    llm = FakeListChatModel(responses=["I'll use the tool."])
    try:
        bound = llm.bind_tools(tools)
        msg = bound.invoke("What is 3+4?")
        print("\n=== bind_tools invoke (fake model) ===")
        print(msg)
    except Exception as exc:
        print(f"\n(bind_tools optional for this fake model: {exc})")

    # Manual tool-call round-trip (what executors implement)
    fake_tool_call = {
        "name": "add",
        "args": {"a": 3, "b": 4},
        "id": "call_add_1",
        "type": "tool_call",
    }
    ai = AIMessage(content="", tool_calls=[fake_tool_call])
    human = HumanMessage(content="Compute 3+4 using the add tool.")

    selected = tool_map[fake_tool_call["name"]]
    result = selected.invoke(fake_tool_call["args"])
    tool_msg = ToolMessage(content=str(result), tool_call_id=fake_tool_call["id"])

    print("\n=== ToolMessage after invocation ===")
    print("AIMessage tool_calls:", ai.tool_calls)
    print("ToolMessage:", tool_msg)

    w = weather_city.invoke({"city": "Oslo", "unit": "celsius"})
    print("\n=== Structured tool return value ===")
    print(w)


if __name__ == "__main__":
    main()
