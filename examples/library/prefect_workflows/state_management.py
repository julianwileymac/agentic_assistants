# requires: prefect
"""Prefect state management and lifecycle hooks.

Demonstrates:
- State types: Completed, Failed, Cancelled
- State change hooks
- Custom state handlers
"""

from __future__ import annotations

import os

os.environ["PREFECT_SERVER_EPHEMERAL_ENABLED"] = "true"


def demo_state_management():
    try:
        from prefect import flow, task

        def on_completion(flow, flow_run, state):
            print(f"  Hook: Flow '{flow.name}' completed in state {state.type}")

        def on_failure(flow, flow_run, state):
            print(f"  Hook: Flow '{flow.name}' failed: {state.message}")

        @task
        def risky_task(should_fail: bool = False) -> str:
            if should_fail:
                raise ValueError("Simulated failure")
            return "success"

        @flow(
            name="stateful-flow",
            on_completion=[on_completion],
            on_failure=[on_failure],
        )
        def stateful_flow(should_fail: bool = False) -> str:
            result = risky_task(should_fail)
            return result

        print("Prefect state management:")
        print("  States: Pending -> Running -> Completed/Failed/Cancelled")
        print("  Hooks: on_completion, on_failure, on_cancellation")
        print("  Custom: on_running hooks for monitoring")
        print()
        try:
            ok = stateful_flow(False)
            print(f"Successful run returned: {ok!r}")
        except Exception as exc:
            print(f"Unexpected error on success path: {exc}")
        print()
        try:
            stateful_flow(True)
        except Exception as exc:
            print(f"Expected failure path (task raises): {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install prefect")


if __name__ == "__main__":
    demo_state_management()
