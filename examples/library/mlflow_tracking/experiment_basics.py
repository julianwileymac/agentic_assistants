# requires: mlflow
"""MLflow experiment tracking with a local file-backed store (no server)."""

from __future__ import annotations

import tempfile
from pathlib import Path


def main() -> None:
    print("MLflow experiment basics: local file store, logging, search_runs")
    print("-" * 60)
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install mlflow"
        )
        return

    root = Path(tempfile.mkdtemp(prefix="mlflow_demo_"))
    uri = root.as_uri()
    mlflow.set_tracking_uri(uri)
    print(f"Tracking URI (local): {uri}")

    mlflow.set_experiment("demo_experiment")
    print("Experiment set: demo_experiment")

    artifact_path = root / "sample_artifact.txt"
    artifact_path.write_text("hello from mlflow artifact\n", encoding="utf-8")

    with mlflow.start_run(run_name="baseline-run") as run:
        mlflow.log_param("model_type", "linear")
        mlflow.log_param("max_iter", 100)
        mlflow.log_metric("train_loss", 0.42, step=0)
        mlflow.log_metric("train_loss", 0.21, step=1)
        mlflow.log_artifact(str(artifact_path))
        run_id = run.info.run_id

    print(f"Logged run id: {run_id}")

    client = MlflowClient(tracking_uri=uri)
    runs = client.search_runs(
        experiment_ids=[client.get_experiment_by_name("demo_experiment").experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=5,
    )
    print(f"search_runs returned {len(runs)} run(s)")
    for r in runs:
        print(f"  run_id={r.info.run_id} status={r.info.status}")
        print(f"    params: {dict(r.data.params)}")
        print(f"    metrics: {dict(r.data.metrics)}")

    print("\nDone. Temp tracking data under:", root)


if __name__ == "__main__":
    main()
