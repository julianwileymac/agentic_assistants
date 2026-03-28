# requires: pyautogen
"""AutoGen 0.2: Docker-backed code execution configuration (config-only demo).

Shows DockerCommandLineCodeExecutor setup with timeout, execution policies, and
how you layer organizational rules (retries, command allowlists) without
starting a container in this script.
"""

from __future__ import annotations

import inspect
import tempfile
from pathlib import Path
from typing import Any


# Application-level policies (not DockerCommandLineCodeExecutor fields): retry
# budget for flaky package installs, and shell patterns you reject in review.
MAX_EXEC_RETRIES = 2
BLOCKED_SHELL_SUBSTRINGS = ("curl ", "wget ", "rm -rf /", "mkfs.", "dd if=")
ALLOWED_SHELL_PREFIXES = ("python ", "pip install ", "echo ", "ls ", "cat ")

# Resource limits are enforced by Docker / orchestration, not by this class.
# Typical `docker run` flags you document alongside the executor:
DOCKER_RESOURCE_HINTS: dict[str, str] = {
    "--memory": "512m",
    "--cpus": "1.0",
    "--pids-limit": "256",
    "--network": "none",  # optional: block egress from the sandbox
}


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
        from autogen.coding.docker_commandline_code_executor import (
            DockerCommandLineCodeExecutor,
        )
    except ImportError:
        print(
            "Install pyautogen to run this example: pip install pyautogen\n\n"
            "Docker executor skeleton (0.2):\n"
            "  from autogen.coding.docker_commandline_code_executor import "
            "DockerCommandLineCodeExecutor\n"
            "  executor = DockerCommandLineCodeExecutor(\n"
            "      image='python:3.11-slim',\n"
            "      timeout=120,\n"
            "      work_dir=Path(tempfile.mkdtemp()),\n"
            "      execution_policies={'python': True, 'bash': False},\n"
            "  )\n"
            "  user = UserProxyAgent(\n"
            "      'user',\n"
            "      human_input_mode='NEVER',\n"
            "      code_execution_config={'executor': executor, 'cache_seed': None},\n"
            "  )\n"
        )
        return

    work_dir = Path(tempfile.mkdtemp(prefix="autogen_docker_cfg_"))
    execution_policies: dict[str, bool] = {
        "python": True,
        "bash": False,
        "shell": False,
        "sh": False,
    }

    # Do not call DockerCommandLineCodeExecutor(...) here: __init__ may start a
    # container on some versions. Only print the kwargs you would pass.
    executor_kwargs: dict[str, Any] = {
        "image": "python:3.11-slim",
        "timeout": 90,
        "work_dir": work_dir,
        "auto_remove": True,
        "stop_container": True,
        "execution_policies": execution_policies,
    }

    print("=== AutoGen 0.2 — Docker sandbox configuration (no container start) ===")
    print("\nDockerCommandLineCodeExecutor.__init__ signature:")
    print(f"  {inspect.signature(DockerCommandLineCodeExecutor.__init__)}")
    print(f"\nwork_dir (host bind target for generated code files):\n  {work_dir.resolve()}")
    print(f"\nplanned executor.timeout: {executor_kwargs['timeout']}")
    print("\nexecution_policies (language gates for extracted code blocks):")
    for lang, allowed in execution_policies.items():
        print(f"  {lang!r}: {allowed}")

    print("\n--- Application security policies (your code / review layer) ---")
    print(f"  MAX_EXEC_RETRIES: {MAX_EXEC_RETRIES}")
    print(f"  BLOCKED_SHELL_SUBSTRINGS (sample): {BLOCKED_SHELL_SUBSTRINGS[:3]} ...")
    print(f"  ALLOWED_SHELL_PREFIXES (sample): {ALLOWED_SHELL_PREFIXES}")

    print("\n--- Resource limits (document for ops; map to docker run / k8s limits) ---")
    for flag, value in DOCKER_RESOURCE_HINTS.items():
        print(f"  {flag}: {value}")

    print(
        """
--- Sandboxed execution flow (when you enable Docker) ---
1. Assistant emits ```python or ```bash blocks; the user proxy extracts them.
2. DockerCommandLineCodeExecutor writes each block to a file under work_dir.
3. A short-lived container runs the file with executor.timeout seconds cap.
4. stdout/stderr + exit code return to the chat as execution feedback.
5. execution_policies disables whole languages (e.g. bash off, python on).
6. Combine with MAX_EXEC_RETRIES and substring blocklists before calling execute.
7. Pin image digests and set CPU/memory/pids/network at deploy time (see hints).

This script only prints configuration; it does not run Docker or pull images.
"""
    )

    llm_config = _mock_llm_config()
    try:
        from autogen import AssistantAgent, UserProxyAgent

        user_proxy = UserProxyAgent(
            name="docker_code_user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            llm_config=llm_config,
        )
        _ = AssistantAgent(
            name="docker_code_assistant",
            system_message="You propose small, safe Python snippets for data tasks.",
            llm_config=llm_config,
        )
        print("\nExample code_execution_config for Docker (set after building executor):")
        print("  {'executor': DockerCommandLineCodeExecutor(**executor_kwargs), 'cache_seed': None}")
        print("\nUserProxyAgent placeholder (code_execution_config=False for this print-only demo):")
        print(f"  name={user_proxy.name!r}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
