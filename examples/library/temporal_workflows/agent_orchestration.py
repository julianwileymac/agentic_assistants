# requires: temporalio

"""Durable multi-step agent workflow: mock LLM, tools, memory, retries, and replay semantics."""

from __future__ import annotations

_TEMPORAL_IMPORT_ERROR: str | None = None
try:
    from datetime import timedelta

    from temporalio import activity, workflow
    from temporalio.common import RetryPolicy
except ImportError as exc:
    _TEMPORAL_IMPORT_ERROR = str(exc)

# In-process memory stand-in for an external store (e.g. DB). Activities may re-run on failure;
# production code should use idempotent writes or dedupe keys.
_AGENT_MEMORY: dict[str, str] = {}


if _TEMPORAL_IMPORT_ERROR is None:

    @activity.defn
    async def call_llm_mock(prompt: str) -> str:
        """Mock LLM: fails once per attempt sequence to demonstrate activity retries."""
        info = activity.info()
        if info.attempt < 2:
            raise RuntimeError("simulated transient LLM outage")
        return f"reasoning[{info.attempt}]: {prompt[:64]}..."

    @activity.defn
    async def run_tool_mock(tool_name: str, args: dict[str, str]) -> str:
        return f"tool={tool_name} ok args={args!r}"

    @activity.defn
    async def persist_agent_memory(session_id: str, key: str, value: str) -> str:
        """Persist key/value for the session (durable workflow schedules this after tool use)."""
        slot = f"{session_id}:{key}"
        _AGENT_MEMORY[slot] = value
        return slot

    @workflow.defn
    class AgentOrchestrationWorkflow:
        @workflow.run
        async def run(self, user_prompt: str, session_id: str) -> str:
            retry = RetryPolicy(
                initial_interval=timedelta(milliseconds=200),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=6,
            )
            thought = await workflow.execute_activity(
                call_llm_mock,
                user_prompt,
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=retry,
            )
            tool_payload = await workflow.execute_activity(
                run_tool_mock,
                "lookup",
                {"query": user_prompt[:48], "from_step": "plan"},
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry,
            )
            await workflow.execute_activity(
                persist_agent_memory,
                session_id,
                "last_tool",
                tool_payload,
                start_to_close_timeout=timedelta(seconds=15),
                retry_policy=retry,
            )
            final = await workflow.execute_activity(
                call_llm_mock,
                f"synthesize: {thought} || {tool_payload}",
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=retry,
            )
            return final


def main() -> None:
    print("Temporal agent orchestration: LLM (mock) + tool + memory + RetryPolicy")
    print("-" * 60)
    if _TEMPORAL_IMPORT_ERROR is not None:
        print(
            "Missing dependency. Install with:\n"
            "  pip install temporalio\n"
            f"Import error: {_TEMPORAL_IMPORT_ERROR}"
        )
        return

    print("Activities:", call_llm_mock.__name__, run_tool_mock.__name__, persist_agent_memory.__name__)
    print("Workflow:", AgentOrchestrationWorkflow.__name__)
    print(
        "\nActivity retries:\n"
        "  call_llm_mock raises on attempt < 2 so Temporal replays the activity until it succeeds.\n"
    )
    print(
        "Worker / process crash recovery:\n"
        "  Workflow code is replayed from history. Activities that already completed are not\n"
        "  executed again; their recorded results are reused. Only the current activity task may\n"
        "  retry on a healthy worker. Start a Worker with workflows=[AgentOrchestrationWorkflow]\n"
        "  and activities=[call_llm_mock, run_tool_mock, persist_agent_memory] on your task queue.\n"
    )
    print(
        "Optional: use temporalio.testing.WorkflowEnvironment.start_time_skipping() for an\n"
        "ephemeral test server and execute_workflow(...) to run this end-to-end locally.\n"
    )


if __name__ == "__main__":
    main()
