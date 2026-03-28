# requires: pyautogen
"""AutoGen 0.2: GroupChat + GroupChatManager with specialized agents.

Three roles (researcher, coder, reviewer) and max_round cap — print-only demo
unless AUTOGEN_LIVE=1 and a model endpoint is available.
"""

from __future__ import annotations

import os
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
        from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent
    except ImportError:
        print(
            "Install pyautogen to run this example: pip install pyautogen\n\n"
            "Group chat skeleton:\n"
            "  from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager\n"
            "  researcher = AssistantAgent('researcher', system_message=..., llm_config=cfg)\n"
            "  coder = AssistantAgent('coder', ...)\n"
            "  reviewer = AssistantAgent('reviewer', ...)\n"
            "  user = UserProxyAgent('user', human_input_mode='NEVER', ...)\n"
            "  group = GroupChat(agents=[user, researcher, coder, reviewer], messages=[], max_round=5)\n"
            "  manager = GroupChatManager(groupchat=group, llm_config=cfg)\n"
            "  user.initiate_chat(manager, message='...')\n"
        )
        return

    llm_config = _mock_llm_config()

    researcher = AssistantAgent(
        name="researcher",
        system_message="You gather facts and cite assumptions briefly. One short paragraph per turn.",
        llm_config=llm_config,
    )
    coder = AssistantAgent(
        name="coder",
        system_message="You propose minimal Python or pseudocode. Stay brief.",
        llm_config=llm_config,
    )
    reviewer = AssistantAgent(
        name="reviewer",
        system_message="You critique prior messages for correctness and clarity. Be constructive.",
        llm_config=llm_config,
    )
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
        llm_config=llm_config,
    )

    max_round = 5
    group_chat = GroupChat(
        agents=[user_proxy, researcher, coder, reviewer],
        messages=[],
        max_round=max_round,
    )
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    print("=== AutoGen 0.2 — GroupChat + GroupChatManager ===")
    print(f"\nmax_round: {max_round}")
    print("\nAgents and roles:")
    for a in (researcher, coder, reviewer):
        print(f"  - {a.name}: {(a.system_message or '')[:80]}...")
    print(f"  - {user_proxy.name}: orchestrates initiate_chat; relays human/automation input")

    print(
        """
--- Group chat flow ---
1. UserProxyAgent starts via initiate_chat(manager, message=...).
2. GroupChatManager chooses the next speaker (default: auto / model-driven routing).
3. Each specialist agent speaks in turn within the shared message list.
4. max_round caps total rounds so discussions cannot run unbounded.
5. Typical pattern: user_proxy + N assistants; manager coordinates who replies next.
"""
    )

    if os.environ.get("AUTOGEN_LIVE") == "1":
        print("\n(AUTOGEN_LIVE=1) Starting group chat (needs working LLM endpoint)...")
        try:
            user_proxy.initiate_chat(
                manager,
                message="Plan a tiny CLI that prints primes up to 50. Keep the discussion under 3 ideas each.",
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Live run failed: {exc!r}")
    else:
        print(
            "\nSkipping live group chat. Export AUTOGEN_LIVE=1 with a valid OpenAI-compatible "
            "server to run initiate_chat end-to-end."
        )


if __name__ == "__main__":
    main()
