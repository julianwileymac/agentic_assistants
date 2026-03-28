# requires: temporalio
"""Temporal workflow + activity definitions and Worker / Client outline."""

from __future__ import annotations

_TEMPORAL_IMPORT_ERROR: str | None = None
try:
    from datetime import timedelta

    from temporalio import activity, workflow
    from temporalio.client import Client
    from temporalio.worker import Worker
except ImportError as exc:
    _TEMPORAL_IMPORT_ERROR = str(exc)

if _TEMPORAL_IMPORT_ERROR is None:

    @activity.defn
    async def say_hello(name: str) -> str:
        return f"Hello, {name}!"

    @workflow.defn
    class GreetingWorkflow:
        @workflow.run
        async def run(self, name: str) -> str:
            return await workflow.execute_activity(
                say_hello,
                name,
                start_to_close_timeout=timedelta(seconds=10),
            )


def main() -> None:
    print("Temporal basics: @workflow.defn, @activity.defn, Worker, Client")
    print("-" * 60)
    if _TEMPORAL_IMPORT_ERROR is not None:
        print(
            "Missing dependency. Install with:\n"
            "  pip install temporalio\n"
            f"Import error: {_TEMPORAL_IMPORT_ERROR}"
        )
        return

    print("Activity registered:", say_hello.__name__)
    print("Workflow class:", GreetingWorkflow.__name__)
    print(
        "\nWorker pattern (runs near your activities; needs Temporal server):\n"
        "  worker = Worker(\n"
        "      client,\n"
        "      task_queue='greeting-tasks',\n"
        "      workflows=[GreetingWorkflow],\n"
        "      activities=[say_hello],\n"
        "  )\n"
        "  await worker.run()\n"
    )
    print(
        "Client pattern (starts a workflow execution):\n"
        "  client = await Client.connect('localhost:7233')\n"
        "  result = await client.execute_workflow(\n"
        "      GreetingWorkflow.run,\n"
        "      'Ada',\n"
        "      id='greeting-ada-1',\n"
        "      task_queue='greeting-tasks',\n"
        "  )\n"
    )
    print("Types for Client / Worker:", Client, Worker)


if __name__ == "__main__":
    main()
