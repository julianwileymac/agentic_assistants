# requires: prefect pydantic
"""Prefect basic flow and task decorators.

Demonstrates:
- @flow and @task decorators
- Parameter validation with Pydantic
- Retries and task dependencies
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field

# Prefect 3.x talks to a Prefect API; ephemeral mode starts a short-lived local server when unset.
# Force on for this educational script so it runs even if a global profile disabled ephemeral mode.
os.environ["PREFECT_SERVER_EPHEMERAL_ENABLED"] = "true"


class ETLParams(BaseModel):
    source_url: str
    batch_size: int = Field(gt=0, default=100)
    max_retries: int = Field(ge=0, default=3)


def demo_basic_flow():
    try:
        from prefect import flow, task

        @task(retries=3, retry_delay_seconds=10)
        def extract(url: str, batch_size: int) -> list[dict]:
            print(f"  Extracting from {url} (batch={batch_size})")
            return [{"id": i, "value": f"record_{i}"} for i in range(batch_size)]

        @task
        def transform(records: list[dict]) -> list[dict]:
            print(f"  Transforming {len(records)} records")
            return [{**r, "processed": True} for r in records]

        @task
        def load(records: list[dict]) -> int:
            print(f"  Loading {len(records)} records")
            return len(records)

        @flow(name="etl-pipeline", log_prints=True)
        def etl_pipeline(params: ETLParams) -> int:
            raw = extract(params.source_url, params.batch_size)
            transformed = transform(raw)
            count = load(transformed)
            return count

        params = ETLParams(source_url="https://api.example.com/data", batch_size=50)
        print(f"Flow 'etl-pipeline' defined with params: {params}")
        print(
            "Running flow (Prefect 3 may start a short-lived local API if PREFECT_API_URL is not set)…"
        )
        try:
            # Prefect 2/3: invoke the @flow function directly; it returns the flow's return value.
            count = etl_pipeline(params)
            print(f"etl_pipeline() returned: {count!r} (records loaded)")
        except ValueError as exc:
            if "PREFECT_API_URL" in str(exc):
                print(
                    "Hint: enable ephemeral API with PREFECT_SERVER_EPHEMERAL_ENABLED=true, "
                    "or run `prefect server start` and set PREFECT_API_URL."
                )
            print(f"Flow run error: {type(exc).__name__}: {exc}")
        except Exception as exc:
            print(f"Flow run error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install prefect pydantic")


if __name__ == "__main__":
    demo_basic_flow()
