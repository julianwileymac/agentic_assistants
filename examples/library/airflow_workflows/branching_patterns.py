# requires: apache-airflow
"""BranchPythonOperator and ShortCircuitOperator: conditional paths in a DAG."""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.python import BranchPythonOperator, ShortCircuitOperator
except ImportError:
    DAG = None  # type: ignore[assignment,misc]

dag = None  # populated below when Airflow is installed


def _pick_path(**context) -> str:
    """Return task_id to follow; other branch tasks are skipped."""
    logical_date = context["logical_date"]
    if logical_date.day % 2 == 0:
        return "even_day_path"
    return "odd_day_path"


def _should_run_heavy(**_) -> bool:
    """Short-circuit: False skips all downstream tasks of this operator."""
    return False


if DAG is not None:
    with DAG(
        dag_id="example_branching_operators",
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        default_args={"owner": "data", "retries": 0},
        tags=["example", "branching"],
    ) as dag:
        start = EmptyOperator(task_id="start")

        branch = BranchPythonOperator(
            task_id="branch_on_day_parity",
            python_callable=_pick_path,
        )

        even_path = EmptyOperator(task_id="even_day_path")
        odd_path = EmptyOperator(task_id="odd_day_path")

        join = EmptyOperator(
            task_id="join_after_branch",
            trigger_rule="none_failed_min_one_success",
        )

        short_circuit = ShortCircuitOperator(
            task_id="skip_heavy_if_disabled",
            python_callable=_should_run_heavy,
        )

        heavy = EmptyOperator(task_id="expensive_scoring_job")
        end = EmptyOperator(task_id="end")

        start >> branch >> [even_path, odd_path] >> join
        join >> short_circuit >> heavy >> end

else:
    dag = None  # type: ignore[assignment]


def main() -> None:
    if dag is None:
        print("Missing dependency. Install with: pip install apache-airflow")
        return
    print("DAG:", dag.dag_id)
    print(
        "BranchPythonOperator: only one of even_day_path / odd_day_path runs; "
        "join uses trigger_rule none_failed_min_one_success.\n"
        "ShortCircuitOperator: when callable returns False, downstream (heavy) is skipped."
    )


if __name__ == "__main__":
    main()
