# requires: temporalio
"""Parent workflow orchestrating parallel child workflows."""

from __future__ import annotations

_TEMPORAL_IMPORT_ERROR: str | None = None
try:
    from temporalio import workflow
except ImportError as exc:
    _TEMPORAL_IMPORT_ERROR = str(exc)

if _TEMPORAL_IMPORT_ERROR is None:

    @workflow.defn
    class ChunkWorkflow:
        @workflow.run
        async def run(self, chunk_id: int) -> str:
            return f"processed_chunk_{chunk_id}"

    @workflow.defn
    class FanOutParentWorkflow:
        @workflow.run
        async def run(self, chunk_ids: list[int]) -> list[str]:
            handles = []
            for cid in chunk_ids:
                h = await workflow.start_child_workflow(
                    ChunkWorkflow.run,
                    cid,
                    id=f"child-chunk-{cid}",
                    task_queue=workflow.info().task_queue,
                )
                handles.append(h)
            return [await h for h in handles]


def main() -> None:
    print("Parent–child Temporal workflow composition")
    print("-" * 60)
    if _TEMPORAL_IMPORT_ERROR is not None:
        print(
            "Missing dependency. Install with:\n"
            "  pip install temporalio\n"
            f"Import error: {_TEMPORAL_IMPORT_ERROR}"
        )
        return

    print("Child workflow:", ChunkWorkflow.__name__)
    print("Parent workflow:", FanOutParentWorkflow.__name__)
    print(
        "\nComposition:\n"
        "  - FanOutParentWorkflow.run receives a list of chunk ids.\n"
        "  - For each id it start_child_workflow(ChunkWorkflow.run, id, ...).\n"
        "  - Child workflows may run in parallel; parent awaits all results.\n"
        "\nTypical extensions:\n"
        "  - Use a dedicated task queue per worker pool.\n"
        "  - Cap concurrency with a semaphore pattern or batched spawning.\n"
    )


if __name__ == "__main__":
    main()
