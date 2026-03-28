# requires: mlflow
"""Custom MLflow pyfunc model: subclass PythonModel, log, load, predict."""

from __future__ import annotations

import tempfile
from pathlib import Path


def main() -> None:
    print("Custom mlflow.pyfunc.PythonModel: log, load, predict")
    print("-" * 60)
    try:
        import mlflow
        import mlflow.pyfunc
        import numpy as np
        import pandas as pd
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install mlflow numpy pandas"
        )
        return

    class MultiplyModel(mlflow.pyfunc.PythonModel):
        """Doubles numeric inputs (list, ndarray, or single-column DataFrame)."""

        def load_context(self, context):  # noqa: ARG002
            self.factor = 2.0

        def predict(self, context, model_input):  # noqa: ARG002
            if isinstance(model_input, pd.DataFrame):
                arr = model_input.iloc[:, 0].to_numpy(dtype=float)
            else:
                arr = np.asarray(model_input, dtype=float)
            return (arr * self.factor).tolist()

    root = Path(tempfile.mkdtemp(prefix="mlflow_pyfunc_"))
    mlflow.set_tracking_uri(root.as_uri())
    mlflow.set_experiment("pyfunc_demo")

    with mlflow.start_run():
        mlflow.pyfunc.log_model(
            artifact_path="custom_model",
            python_model=MultiplyModel(),
        )
        run_id = mlflow.active_run().info.run_id

    model_uri = f"runs:/{run_id}/custom_model"
    loaded = mlflow.pyfunc.load_model(model_uri)

    sample_df = pd.DataFrame({"x": [1.0, 2.5, 3.0]})
    out_df = loaded.predict(sample_df)
    print("Predict on DataFrame:", out_df)

    out_list = loaded.predict([10.0, 20.0])
    print("Predict on list:", out_list)
    print("\nTemp store:", root)


if __name__ == "__main__":
    main()
