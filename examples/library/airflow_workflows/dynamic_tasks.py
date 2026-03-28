# requires: apache-airflow
"""Dynamic task mapping with `.expand()` and parameterized TaskGroups."""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow.decorators import dag, task, task_group
except ImportError:
    dag = None  # type: ignore[assignment]
    task = None  # type: ignore[assignment]
    task_group = None  # type: ignore[assignment]


if dag is not None and task is not None and task_group is not None:

    @dag(
        dag_id="example_dynamic_tasks",
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        default_args={"owner": "data", "retries": 0},
        tags=["example", "dynamic"],
    )
    def dynamic_parallelism_demo():
        @task
        def list_partitions() -> list[str]:
            return ["us-east", "eu-west", "ap-south"]

        @task
        def process_partition(region: str) -> str:
            return f"processed-{region}"

        regions = list_partitions()
        process_partition.expand(region=regions)

        @task_group(group_id="shard_group")
        def shard_pipeline(shard_id: int):
            @task
            def prep() -> int:
                return shard_id

            @task
            def compute(x: int) -> int:
                return x * x

            compute(prep())

        shard_pipeline.expand(shard_id=[1, 2, 3])

    dag = dynamic_parallelism_demo()

else:
    dag = None  # type: ignore[assignment]


def main() -> None:
    if dag is None:
        print("Missing dependency. Install with: pip install apache-airflow")
        return
    print("DAG:", dag.dag_id)
    print(
        "Patterns shown:\n"
        "  - process_partition.expand(region=regions) maps over an XCom list.\n"
        "  - Fan-in of mapped outputs uses a reduce pattern or @task.partial; "
        "omitted here for clarity.\n"
        "  - task_group(...).expand(shard_id=[...]) duplicates a subgraph per id."
    )


if __name__ == "__main__":
    main()
