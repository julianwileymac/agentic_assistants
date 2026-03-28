# requires: bentoml scikit-learn joblib numpy
"""BentoML model packaging: `bentoml.models.create`, sklearn estimator, `@bentoml.service`.

Run `python model_packaging.py` once to register `sklearn_linear_demo:latest` in the
Model Store, then serve the module-level class, for example:

  bentoml serve examples.library.bentoml_serving.model_packaging:LinearRegressionService
"""

from __future__ import annotations

import pathlib

MODEL_NAME = "sklearn_linear_demo"

try:
    import bentoml
    import joblib
    import numpy as np
    from bentoml.models import BentoModel
    from sklearn.linear_model import LinearRegression
except ImportError:
    bentoml = None  # type: ignore[assignment]
    joblib = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    BentoModel = None  # type: ignore[assignment]
    LinearRegression = None  # type: ignore[assignment]


if bentoml is not None and BentoModel is not None:

    @bentoml.service(name="linear_regression_service")
    class LinearRegressionService:
        """Loads the estimator from the Model Store; declare model ref at class scope."""

        bento_model = BentoModel(f"{MODEL_NAME}:latest")

        def __init__(self) -> None:
            assert joblib is not None
            self._estimator = joblib.load(self.bento_model.path_of("model.pkl"))

        @bentoml.api
        def predict(self, features: np.ndarray) -> np.ndarray:
            return self._estimator.predict(features)

else:

    class LinearRegressionService:  # type: ignore[no-redef]
        """Placeholder when bentoml / sklearn are not installed."""

        pass


def main() -> None:
    if bentoml is None or joblib is None or np is None or LinearRegression is None:
        print("Missing dependency (need bentoml, scikit-learn, joblib, numpy).")
        print("Install with: pip install bentoml scikit-learn joblib numpy")
        return

    X = np.array([[1.0], [2.0], [3.0]], dtype=np.float64)
    y = np.array([2.0, 4.0, 6.0], dtype=np.float64)
    model = LinearRegression().fit(X, y)

    with bentoml.models.create(name=MODEL_NAME) as model_ref:
        artifact = pathlib.Path(model_ref.path) / "model.pkl"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, artifact)
    print(f"Registered model in Model Store: {MODEL_NAME}:latest")

    print(
        "\nRunner pattern (sklearn integration - alternative to raw joblib):\n"
        "  saved = bentoml.sklearn.save_model('my_sklearn_model', estimator)\n"
        "  runner = bentoml.sklearn.get('my_sklearn_model:latest').to_runner()\n"
        "  # runner.predict.run(ndarray) inside @bentoml.api or async runner.async_run"
    )
    print(
        "\nServe this module's service class with:\n"
        "  bentoml serve ...model_packaging:LinearRegressionService"
    )


if __name__ == "__main__":
    main()
