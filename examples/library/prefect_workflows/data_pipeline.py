# requires: prefect
"""Prefect ETL data pipeline with caching and persistence.

Demonstrates:
- Task caching with cache_key_fn
- Result persistence
- Complex task dependencies
"""

from __future__ import annotations

import os
from datetime import timedelta

os.environ["PREFECT_SERVER_EPHEMERAL_ENABLED"] = "true"


def demo_data_pipeline():
    try:
        from prefect import flow, task
        from prefect.tasks import task_input_hash

        @task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
        def fetch_data(endpoint: str) -> list[dict]:
            print(f"  Fetching from {endpoint} (cached for 1h)")
            return [{"id": i, "raw": f"data_{i}"} for i in range(10)]

        @task
        def validate(records: list[dict]) -> list[dict]:
            valid = [r for r in records if r.get("id") is not None]
            print(f"  Validated: {len(valid)}/{len(records)} records")
            return valid

        @task
        def enrich(records: list[dict]) -> list[dict]:
            return [{**r, "enriched": True, "score": r["id"] * 0.1} for r in records]

        @task(persist_result=True)
        def store(records: list[dict]) -> int:
            print(f"  Stored {len(records)} records (result persisted)")
            return len(records)

        @flow(name="data-pipeline")
        def data_pipeline(endpoint: str = "https://api.example.com") -> int:
            raw = fetch_data(endpoint)
            valid = validate(raw)
            enriched = enrich(valid)
            return store(enriched)

        print("Data pipeline: fetch -> validate -> enrich -> store")
        print("  Features: task caching, result persistence")
        print()
        try:
            stored = data_pipeline("https://api.example.com/demo")
            print(f"Pipeline finished. Records stored (return value): {stored!r}")
        except Exception as exc:
            print(
                "Pipeline run failed (persist_result/cache may need Prefect results config): "
                f"{type(exc).__name__}: {exc}"
            )

    except ImportError:
        print("Install: pip install prefect")


if __name__ == "__main__":
    demo_data_pipeline()
