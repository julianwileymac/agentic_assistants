# requires: pyautogen
"""AutoGen 0.2: human-in-the-loop gates, turn limits, and termination callbacks.

Covers UserProxyAgent human_input modes, max_consecutive_auto_reply as a turn
budget, and is_termination_msg patterns (keyword-based stop signals).
"""

from __future__ import annotations

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


def is_termination_msg_keyword(msg: dict[str, Any]) -> bool:
    """Stop when the model or human emits an agreed keyword (case-insensitive)."""
    content = (msg.get("content") or "").strip().upper()
    if not content:
        return False
    stop_tokens = ("TERMINATE", "APPROVED", "REJECTED", "STOP_SESSION")
    return any(tok in content for tok in stop_tokens)


def is_termination_msg_short_reply(msg: dict[str, Any]) -> bool:
    """Stop after a very short final acknowledgment (demo heuristic)."""
    content = (msg.get("content") or "").strip()
    return len(content) > 0 and len(content) < 8 and content.lower() in {"ok", "done", "lgtm"}


def main() -> None:
    try:
        from autogen import AssistantAgent, UserProxyAgent
    except ImportError:
        print(
            "Install pyautogen to run this example: pip install pyautogen\n\n"
            "Human-in-the-loop patterns:\n"
            "  user = UserProxyAgent(\n"
            "      'user',\n"
            "      human_input_mode='ALWAYS',  # or 'TERMINATE' / 'NEVER'\n"
            "      max_consecutive_auto_reply=4,\n"
            "      is_termination_msg=lambda m: 'TERMINATE' in (m.get('content') or ''),\n"
            "  )\n"
            "  assistant = AssistantAgent(\n"
            "      'assistant',\n"
            "      is_termination_msg=...,  # mirror or stricter policy\n"
            "  )\n"
        )
        return

    llm_config = _mock_llm_config()

    approval_user = UserProxyAgent(
        name="approval_user",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=6,
        code_execution_config=False,
        llm_config=llm_config,
        is_termination_msg=is_termination_msg_keyword,
    )

    gate_user = UserProxyAgent(
        name="gate_user",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
        llm_config=llm_config,
        is_termination_msg=is_termination_msg_short_reply,
    )

    assistant = AssistantAgent(
        name="policy_assistant",
        system_message=(
            "You propose one step at a time. When the human approves, summarize and "
            "say TERMINATE to end cleanly."
        ),
        llm_config=llm_config,
        is_termination_msg=is_termination_msg_keyword,
    )

    print("=== AutoGen 0.2 — human proxy, turns, termination callbacks ===")

    print("\n--- Human input modes (UserProxyAgent) ---")
    print("  NEVER:  no prompts; fully autonomous proxy.")
    print("  ALWAYS: prompt before each reply — approval gate every turn.")
    print("  TERMINATE: prompt only when a termination condition fires.")

    print("\n--- Turn budget ---")
    print(
        "  max_consecutive_auto_reply caps how many automated replies the user proxy "
        "sends before pausing or requiring human input (pair with human_input_mode)."
    )
    print(f"  approval_user.max_consecutive_auto_reply: {approval_user.max_consecutive_auto_reply}")
    print(f"  gate_user.max_consecutive_auto_reply: {gate_user.max_consecutive_auto_reply}")

    print("\n--- is_termination_msg callbacks ---")
    demo_msgs: list[dict[str, Any]] = [
        {"content": "Here is the plan ..."},
        {"content": "APPROVED"},
        {"content": "ok"},
    ]
    for m in demo_msgs:
        print(
            f"  msg={m['content']!r}  -> keyword_stop={is_termination_msg_keyword(m)}  "
            f"short_stop={is_termination_msg_short_reply(m)}"
        )

    print(
        """
--- Human feedback integration patterns ---
1. Gate risky tools: human_input_mode='ALWAYS' on the proxy that runs tools/code.
2. Summarize-then-exit: assistant ends with TERMINATE after human says APPROVED.
3. Dual callbacks: stricter is_termination_msg on assistant, looser on user proxy.
4. Combine with max_consecutive_auto_reply so runs cannot loop unbounded.

Skipping live initiate_chat (needs a working LLM). Wire approval_user or gate_user
as the chat entrypoint with initiate_chat(assistant, message=...).
"""
    )

    term_cb = getattr(assistant, "is_termination_msg", None)
    print("\nAssistant is_termination_msg:", term_cb)


if __name__ == "__main__":
    main()
