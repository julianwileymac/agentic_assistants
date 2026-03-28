# requires: apache-airflow
"""Airflow TaskFlow basics: `@dag` / `@task`, schedule, and catchup settings."""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow.decorators import dag, task
except ImportError:
    dag = None  # type: ignore[assignment]
    task = None  # type: ignore[assignment]


if dag is not None and task is not None:

    @dag(
        dag_id="example_taskflow_basic",
        start_date=datetime(2024, 1, 1),
        schedule="@daily",
        catchup=False,
        default_args={
            "owner": "data",
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        tags=["example", "taskflow"],
        doc_md="Minimal TaskFlow DAG: extract -> transform -> load.",
    )
    def example_taskflow_basic():
        @task
        def extract() -> dict[str, int]:
            return {"rows": 100}

        @task
        def transform(meta: dict[str, int]) -> int:
            return meta["rows"] * 2

        @task
        def load(processed_count: int) -> None:
            print(f"Would load {processed_count} records")

        meta = extract()
        count = transform(meta)
        load(count)

    dag = example_taskflow_basic()

else:
    dag = None  # type: ignore[assignment]


def main() -> None:
    if dag is None:
        print("Missing dependency. Install with: pip install apache-airflow")
        return
    print("DAG defined:", dag.dag_id)
    print("schedule_interval:", getattr(dag, "schedule_interval", None))
    print("catchup:", dag.catchup)


if __name__ == "__main__":
    main()
