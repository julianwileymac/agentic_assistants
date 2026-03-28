# requires: pyautogen
"""AutoGen 0.2: register_for_llm + register_for_execution tool pattern.

Assistant registers tool schema for the model; UserProxy registers runnable implementations.
"""

from __future__ import annotations

import json
from typing import Any


def _mock_llm_config() -> dict[str, Any]:
    return {
        "config_list": [
            {
                "model": "mock-gpt",
                "api_key": "mock-key",
                "base_url": "http://127.0.0.1:11434/v1",
            }
        ],
        "cache_seed": None,
    }


def main() -> None:
    try:
        from autogen import AssistantAgent, UserProxyAgent
    except ImportError:
        print(
            "Install pyautogen to run this example: pip install pyautogen\n\n"
            "Tool registration pattern:\n"
            "  @user_proxy.register_for_execution(name='calculator')\n"
            "  @assistant.register_for_llm(name='calculator', description='...')\n"
            "  def calculator(expression: str) -> str:\n"
            "      ...\n"
        )
        return

    llm_config = _mock_llm_config()

    assistant = AssistantAgent(
        name="tool_assistant",
        system_message="You may call tools when they help. For demos, prefer tool calls over guessing.",
        llm_config=llm_config,
    )
    user_proxy = UserProxyAgent(
        name="tool_executor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=False,
        llm_config=llm_config,
    )

    @user_proxy.register_for_execution(name="calculator")
    @assistant.register_for_llm(
        name="calculator",
        description="Evaluate a simple arithmetic expression with + - * / and parentheses. "
        "Example: '(2 + 3) * 4'.",
    )
    def calculator(expression: str) -> str:
        """Safe-ish demo: only allow digits, operators, parentheses, spaces."""
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return json.dumps({"error": "unsupported characters", "expression": expression})
        try:
            value = eval(expression, {"__builtins__": {}}, {})  # noqa: S307 — educational demo
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": str(exc), "expression": expression})
        return json.dumps({"result": value})

    @user_proxy.register_for_execution(name="weather_lookup")
    @assistant.register_for_llm(
        name="weather_lookup",
        description="Mock weather lookup by city name (no external API).",
    )
    def weather_lookup(city: str) -> str:
        fake_db = {
            "london": {"temp_c": 12, "condition": "cloudy"},
            "tokyo": {"temp_c": 22, "condition": "clear"},
        }
        key = city.strip().lower()
        data = fake_db.get(key, {"temp_c": 20, "condition": "unknown (demo default)"})
        return json.dumps({"city": city, **data})

    print("=== AutoGen 0.2 — tool registration (LLM schema + execution) ===")
    print(
        """
Decorators applied bottom-up on the function object:
  1) register_for_llm on AssistantAgent → exposes JSON tool schema to the model.
  2) register_for_execution on UserProxyAgent → binds the Python callable that runs
     when the model issues a tool call.

At runtime:
  - Model emits tool_calls → framework dispatches to the user proxy executor.
  - Tool return strings are appended as tool/function messages for the assistant's next turn.
"""
    )

    # Surface registered tool metadata where the API exposes it (version-dependent).
    for label, agent in ("assistant", assistant), ("user_proxy", user_proxy):
        fn_map = getattr(agent, "_function_map", None) or getattr(agent, "function_map", None)
        print(f"\n--- {label} function_map keys ---")
        if fn_map:
            print(f"  {list(fn_map.keys())}")
        else:
            print("  (inspect your pyautogen version; tools are still registered for chat.)")

    print("\n--- Sample local tool invocations (no LLM) ---")
    print("  calculator('(1+2)*3'):", calculator("(1+2)*3"))
    print("  weather_lookup('London'):", weather_lookup("London"))


if __name__ == "__main__":
    main()
