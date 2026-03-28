# requires: temporalio
"""Long-running agentic workflow: LLM, tools, aggregation with retries."""

from __future__ import annotations

_TEMPORAL_IMPORT_ERROR: str | None = None
try:
    from datetime import timedelta

    from temporalio import activity, workflow
    from temporalio.common import RetryPolicy
except ImportError as exc:
    _TEMPORAL_IMPORT_ERROR = str(exc)

if _TEMPORAL_IMPORT_ERROR is None:

    @activity.defn
    async def call_llm(prompt: str) -> str:
        # Stand-in for an LLM API call (deterministic placeholder for demos).
        return f"[llm-response] processed: {prompt[:48]}..."

    @activity.defn
    async def run_tool(tool_name: str, args: dict) -> str:
        return f"tool={tool_name} result={args}"

    @activity.defn
    async def aggregate_results(parts: list[str]) -> str:
        return " | ".join(parts)

    @workflow.defn
    class AgentWorkflow:
        @workflow.run
        async def run(self, user_prompt: str) -> str:
            retry = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            )
            draft = await workflow.execute_activity(
                call_llm,
                user_prompt,
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry,
            )
            tool_out = await workflow.execute_activity(
                run_tool,
                "lookup",
                {"query": user_prompt[:32]},
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )
            return await workflow.execute_activity(
                aggregate_results,
                [draft, tool_out],
                start_to_close_timeout=timedelta(seconds=30),
            )


def main() -> None:
    print("Durable agentic Temporal workflow (activities + retries)")
    print("-" * 60)
    if _TEMPORAL_IMPORT_ERROR is not None:
        print(
            "Missing dependency. Install with:\n"
            "  pip install temporalio\n"
            f"Import error: {_TEMPORAL_IMPORT_ERROR}"
        )
        return

    print("Activities:", call_llm.__name__, run_tool.__name__, aggregate_results.__name__)
    print("Workflow:", AgentWorkflow.__name__)
    print(
        "\nDefinition summary:\n"
        "  1) call_llm — slow / flaky step; generous timeout + RetryPolicy.\n"
        "  2) run_tool — side-effecting tool execution; shorter timeout.\n"
        "  3) aggregate_results — merges partial outputs for the final reply.\n"
        "\nTemporal replays workflow code deterministically; put non-deterministic\n"
        "work (network I/O, randomness) inside activities only.\n"
    )


if __name__ == "__main__":
    main()
