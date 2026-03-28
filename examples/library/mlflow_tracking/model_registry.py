# requires: mlflow
"""MLflow model registry: log sklearn-like model, register, transition stages."""

from __future__ import annotations

import tempfile
from pathlib import Path


def main() -> None:
    print("MLflow model registry with mlflow.pyfunc and stage transitions")
    print("-" * 60)
    try:
        import mlflow
        import numpy as np
        from mlflow.tracking import MlflowClient
        from sklearn.dummy import DummyClassifier
    except ImportError as e:
        print(
            "Missing dependency. Install with:\n"
            "  pip install mlflow scikit-learn numpy\n"
            f"Import error: {e}"
        )
        return

    root = Path(tempfile.mkdtemp(prefix="mlflow_registry_"))
    mlflow.set_tracking_uri(root.as_uri())
    mlflow.set_experiment("registry_demo")

    X = np.array([[0], [1], [2], [3]])
    y = np.array([0, 0, 1, 1])
    model = DummyClassifier(strategy="most_frequent")
    model.fit(X, y)

    registered_name = "demo_sklearn_classifier"

    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name=registered_name)
        run_id = run.info.run_id

    print(f"Logged model under run {run_id} and registered as '{registered_name}'")

    client = MlflowClient(tracking_uri=root.as_uri())
    versions = client.search_model_versions(f"name='{registered_name}'")
    print(f"Registry has {len(versions)} version(s) for this model")
    for mv in versions:
        print(f"  version={mv.version} stage={mv.current_stage} run_id={mv.run_id}")

    if versions:
        mv = max(versions, key=lambda v: int(v.version))
        client.transition_model_version_stage(
            name=registered_name,
            version=int(mv.version),
            stage="Staging",
        )
        client.transition_model_version_stage(
            name=registered_name,
            version=int(mv.version),
            stage="Production",
            archive_existing_versions=True,
        )
        refreshed = client.get_model_version(name=registered_name, version=mv.version)
        print(f"After transitions: version {refreshed.version} stage={refreshed.current_stage}")

    # Load as pyfunc and predict
    model_uri = f"runs:/{run_id}/model"
    pyfunc_model = mlflow.pyfunc.load_model(model_uri)
    preds = pyfunc_model.predict(np.array([[5]]))
    print(f"pyfunc.load_model predict sample: {preds}")

    print("\nFinal registry snapshot:")
    for mv in client.search_model_versions(f"name='{registered_name}'"):
        print(f"  {registered_name} v{mv.version} stage={mv.current_stage}")
    print("\nTemp store:", root)


if __name__ == "__main__":
    main()
