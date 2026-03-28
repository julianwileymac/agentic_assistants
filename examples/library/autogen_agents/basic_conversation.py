# requires: pyautogen
"""AutoGen 0.2 (pyautogen): AssistantAgent + UserProxyAgent and initiate_chat.

Uses a mock LLM config (no real API key required for inspecting setup).
Live chat only runs if AUTOGEN_LIVE=1 and a reachable endpoint is configured.
"""

from __future__ import annotations

import os
from typing import Any


def _mock_llm_config() -> dict[str, Any]:
    """Config list for local/mock testing (e.g. LM Studio, vLLM, or ollama OpenAI shim)."""
    return {
        "config_list": [
            {
                "model": "mock-gpt",
                "api_key": "mock-key-not-used-unless-you-enable-live-run",
                "base_url": "http://127.0.0.1:11434/v1",
            }
        ],
        "temperature": 0.2,
        "cache_seed": None,
    }


def _print_agent_summary(assistant: Any, user_proxy: Any) -> None:
    print("\n--- AssistantAgent (LLM side) ---")
    print(f"  name: {assistant.name}")
    print(f"  human_input_mode: {getattr(assistant, 'human_input_mode', 'n/a')}")
    print(f"  max_consecutive_auto_reply: {getattr(assistant, 'max_consecutive_auto_reply', 'n/a')}")
    print(f"  llm_config keys: {list((assistant.llm_config or {}).keys())}")

    print("\n--- UserProxyAgent (human / tool / code proxy) ---")
    print(f"  name: {user_proxy.name}")
    print(f"  human_input_mode: {user_proxy.human_input_mode}")
    print(f"  max_consecutive_auto_reply: {user_proxy.max_consecutive_auto_reply}")
    print(f"  code_execution_config: {getattr(user_proxy, 'code_execution_config', None)}")


def _explain_flow() -> None:
    print(
        """
--- Conversation flow (AutoGen 0.2) ---
1. UserProxyAgent receives the initial user message via initiate_chat().
2. Messages are sent to AssistantAgent; the LLM replies.
3. UserProxyAgent relays assistant output back; loop continues until termination
   (e.g. max rounds, keyword, or is_termination_msg).
4. With human_input_mode="NEVER", the user proxy does not prompt stdin; it auto-replies
   so the demo can run unattended (still needs a working model endpoint for real turns).
5. max_consecutive_auto_reply limits how many automatic proxy replies occur per turn,
   bounding cost and runaway loops in automation mode.
"""
    )


def main() -> None:
    try:
        from autogen import AssistantAgent, UserProxyAgent
    except ImportError:
        print(
            "Install pyautogen to run this example: pip install pyautogen\n\n"
            "Expected structure (AutoGen 0.2 API):\n"
            "  from autogen import AssistantAgent, UserProxyAgent\n"
            "  llm_config = {'config_list': [{...}], 'cache_seed': None}\n"
            "  assistant = AssistantAgent('assistant', llm_config=llm_config)\n"
            "  user = UserProxyAgent('user', human_input_mode='NEVER', max_consecutive_auto_reply=2)\n"
            "  user.initiate_chat(assistant, message='Hello', ...)\n"
        )
        return

    llm_config = _mock_llm_config()

    assistant = AssistantAgent(
        name="demo_assistant",
        system_message="You are a concise assistant for a demo. Keep replies short.",
        llm_config=llm_config,
    )

    user_proxy = UserProxyAgent(
        name="demo_user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        code_execution_config=False,
        llm_config=llm_config,
    )

    print("=== AutoGen 0.2 — basic two-agent chat setup ===")
    _print_agent_summary(assistant, user_proxy)
    _explain_flow()

    print("\n--- initiate_chat pattern (code you would run) ---")
    print(
        "  user_proxy.initiate_chat(\n"
        "      assistant,\n"
        "      message='Summarize what AutoGen UserProxyAgent does in one sentence.',\n"
        "  )"
    )

    if os.environ.get("AUTOGEN_LIVE") == "1":
        print("\n(AUTOGEN_LIVE=1) Attempting live initiate_chat against configured base_url...")
        try:
            user_proxy.initiate_chat(
                assistant,
                message="Reply with exactly: OK_DEMO",
            )
        except Exception as exc:  # noqa: BLE001 — demo boundary
            print(f"Live run failed (expected without a local LLM): {exc!r}")
    else:
        print(
            "\nSkipping live LLM calls. Set AUTOGEN_LIVE=1 and point config_list to a "
            "running OpenAI-compatible server to exercise initiate_chat."
        )


if __name__ == "__main__":
    main()
