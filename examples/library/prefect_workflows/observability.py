# requires: prefect opentelemetry-api
"""Prefect + OpenTelemetry observability integration.

Demonstrates:
- Tracing flows and tasks with OpenTelemetry
- Custom metrics and structured logging
- Integration with Logfire/OTEL collectors
"""

from __future__ import annotations

import os

os.environ["PREFECT_SERVER_EPHEMERAL_ENABLED"] = "true"


def demo_observability():
    try:
        from prefect import flow, task

        @task
        def traced_extract(source: str) -> list[dict]:
            """Task automatically traced by Prefect."""
            return [{"data": f"from_{source}"}]

        @task
        def traced_transform(records: list[dict]) -> list[dict]:
            return [{**r, "transformed": True} for r in records]

        @flow(name="observable-pipeline", log_prints=True)
        def observable_pipeline(source: str = "api") -> int:
            data = traced_extract(source)
            result = traced_transform(data)
            print(f"Processed {len(result)} records")
            return len(result)

        print("Prefect Observability:")
        print("  - Flows and tasks are auto-traced")
        print("  - Prefect UI shows run history, logs, and task states")
        print("  - Integrate with OTEL: set PREFECT_LOGGING_EXTRA_LOGGERS")
        print("  - Logfire: logfire.instrument_prefect() for deep tracing")
        print()
        try:
            n = observable_pipeline("demo-source")
            print(f"Observable pipeline returned: {n!r}")
        except Exception as exc:
            print(f"Flow run error: {exc}")

    except ImportError:
        print("Install: pip install prefect")


if __name__ == "__main__":
    demo_observability()
