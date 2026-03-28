# requires: mlflow, scikit-learn
"""mlflow.sklearn.autolog(): params and metrics captured automatically."""

from __future__ import annotations

import tempfile
from pathlib import Path


def main() -> None:
    print("MLflow sklearn autolog on LogisticRegression + synthetic data")
    print("-" * 60)
    try:
        import mlflow
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install mlflow scikit-learn numpy"
        )
        return

    root = Path(tempfile.mkdtemp(prefix="mlflow_autolog_"))
    mlflow.set_tracking_uri(root.as_uri())
    mlflow.set_experiment("autolog_demo")

    mlflow.sklearn.autolog(log_input_examples=False, silent=True)

    rng = np.random.default_rng(42)
    X = rng.standard_normal((200, 4))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0
    )

    with mlflow.start_run(run_name="lr-autolog") as run:
        clf = LogisticRegression(max_iter=200, C=1.5)
        clf.fit(X_train, y_train)
        train_acc = float(clf.score(X_train, y_train))
        test_acc = float(clf.score(X_test, y_test))
        mlflow.log_metric("manual_train_acc", train_acc)
        mlflow.log_metric("manual_test_acc", test_acc)
        run_id = run.info.run_id

    mlflow.sklearn.autolog(disable=True)

    run = mlflow.get_run(run_id)
    print(f"Run id: {run_id}")
    print("Autologged params (subset):", {k: run.data.params[k] for k in sorted(run.data.params) if k in ("C", "max_iter", "solver")})
    print("Autologged metrics (keys):", sorted(run.data.metrics.keys()))
    print("Manual metrics logged:", {k: run.data.metrics[k] for k in ("manual_train_acc", "manual_test_acc") if k in run.data.metrics})
    print("\nTemp tracking store:", root)


if __name__ == "__main__":
    main()
