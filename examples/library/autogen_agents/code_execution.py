# requires: pyautogen
"""AutoGen 0.2: UserProxyAgent with code_execution_config and local work_dir.

Shows how the user proxy can run generated Python in an isolated working directory.
No network required to demonstrate configuration; execution uses the local interpreter.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
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
            "Code execution pattern:\n"
            "  work_dir = Path(tempfile.mkdtemp())\n"
            "  user = UserProxyAgent(\n"
            "      'user',\n"
            "      human_input_mode='NEVER',\n"
            "      code_execution_config={\n"
            "          'work_dir': str(work_dir),\n"
            "          'use_docker': False,\n"
            "      },\n"
            "  )\n"
            "  # Assistant proposes Python in chat; user proxy executes it under work_dir.\n"
        )
        return

    work_dir = Path(tempfile.mkdtemp(prefix="autogen_code_demo_"))
    llm_config = _mock_llm_config()

    code_execution_config: dict[str, Any] = {
        "work_dir": str(work_dir),
        "use_docker": False,
        "timeout": 60,
    }

    assistant = AssistantAgent(
        name="coder_assistant",
        system_message=(
            "You write short Python snippets. When asked for code, put it in a single "
            "markdown fenced block so the user proxy can execute it."
        ),
        llm_config=llm_config,
    )

    user_proxy = UserProxyAgent(
        name="code_runner_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=code_execution_config,
        llm_config=llm_config,
    )

    print("=== AutoGen 0.2 — code execution agent setup ===")
    print(f"\nwork_dir (isolated sandbox):\n  {work_dir.resolve()}")
    print("\ncode_execution_config:")
    for k, v in code_execution_config.items():
        print(f"  {k}: {v!r}")

    print(
        """
--- Execution flow ---
1. AssistantAgent proposes Python (often inside ```python ... ``` blocks).
2. UserProxyAgent parses those blocks and runs them as subprocesses/scripts under work_dir.
3. stdout/stderr is captured and fed back into the chat as execution results.
4. The assistant can iterate (fix imports, adjust logic) based on errors.
5. use_docker=False runs on the host Python — convenient for demos; use Docker in prod
   for stronger isolation.

--- Agent pairing ---
- Assistant: reasoning + code generation (LLM).
- User proxy: executes code when the conversation contains executable blocks.
"""
    )

    demo_script = work_dir / "hello_autogen.py"
    demo_script.write_text('print("hello from autogen work_dir")', encoding="utf-8")
    print(f"\nWrote sample file for illustration: {demo_script}")
    print("(In a full chat, the LLM would generate similar files via executed code.)")

    print("\nUserProxyAgent summary:")
    print(f"  name: {user_proxy.name}")
    print(f"  code_execution_config: {user_proxy.code_execution_config}")


if __name__ == "__main__":
    main()
