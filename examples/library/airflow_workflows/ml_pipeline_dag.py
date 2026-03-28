# requires: apache-airflow
"""Multi-step ML DAG: ingest -> feature engineering -> train -> evaluate -> deploy."""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow.decorators import dag, task
except ImportError:
    dag = None  # type: ignore[assignment]
    task = None  # type: ignore[assignment]


if dag is not None and task is not None:

    @dag(
        dag_id="example_ml_pipeline",
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        default_args={
            "owner": "ml",
            "retries": 1,
            "retry_delay": timedelta(minutes=10),
        },
        tags=["example", "ml"],
    )
    def ml_training_pipeline():
        @task
        def ingest_raw() -> str:
            return "s3://datalake/raw/dt={{ ds }}"

        @task
        def feature_engineering(raw_uri: str) -> str:
            return f"{raw_uri}/features/vectorized"

        @task
        def train_model(feature_uri: str) -> str:
            return f"models/model_from_{feature_uri.split('/')[-2]}.pkl"

        @task
        def evaluate_model(model_path: str) -> dict[str, float]:
            return {"auc": 0.87, "logloss": 0.42}

        @task
        def deploy_model(model_path: str) -> None:
            print(f"Promote {model_path} to serving (stub)")

        raw = ingest_raw()
        features = feature_engineering(raw)
        model_artifact = train_model(features)
        metrics = evaluate_model(model_artifact)
        _ = metrics  # could gate deploy on metric thresholds
        deploy_model(model_artifact)

    dag = ml_training_pipeline()

else:
    dag = None  # type: ignore[assignment]


def main() -> None:
    if dag is None:
        print("Missing dependency. Install with: pip install apache-airflow")
        return
    print("DAG:", dag.dag_id)
    for t in dag.task_ids:
        print("  task:", t)


if __name__ == "__main__":
    main()
