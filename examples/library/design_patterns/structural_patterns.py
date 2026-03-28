# requires: (no external deps - uses core package only)

"""ML-oriented structural patterns: AdapterBase, decorators, LazyProxy."""

from __future__ import annotations

import logging
import time
from typing import Any, List

try:
    from agentic_assistants.core.patterns import (
        AdapterBase,
        CachingDecorator,
        LazyProxy,
        LoggingDecorator,
    )
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class MockTensorFlowModel:
        """Minimal stand-in for a TF/Keras-style model with a non-sklearn surface API."""

        def __init__(self) -> None:
            self._trained = False

        def compile_model(self, optimizer: str = "adam") -> None:
            self._optimizer = optimizer

        def train_on_batch(self, x: List[List[float]], y: List[float]) -> float:
            self._trained = True
            return 0.25

        def forward_logits(self, x: List[List[float]]) -> List[float]:
            if not self._trained:
                raise RuntimeError("Model not trained")
            return [sum(row) * 0.1 for row in x]

    class TensorFlowToSklearnAdapter(AdapterBase[MockTensorFlowModel, List[float]]):
        """Adapts TF-style train_on_batch / forward_logits to sklearn-like fit / predict."""

        def fit(
            self, X: List[List[float]], y: List[float] | None = None
        ) -> "TensorFlowToSklearnAdapter":
            if y is None:
                y = [0.0] * len(X)
            self._adaptee.train_on_batch(X, y)
            return self

        def predict(self, X: List[List[float]]) -> List[float]:
            return self.adapt(X)

        def adapt(self, *args: Any, **kwargs: Any) -> List[float]:
            (X,) = args
            return self._adaptee.forward_logits(X)

    class MockSklearnStyleModel:
        """Simple estimators we decorate at the method level via DecoratorBase.call."""

        def predict(self, X: List[List[float]]) -> List[int]:
            time.sleep(0.02)
            return [1 if sum(row) > 2 else 0 for row in X]

    class PredictMethodBridge:
        """Exposes ``predict`` so outer ``DecoratorBase`` layers can call into inner ``.call()``."""

        def __init__(self, inner: LoggingDecorator[MockSklearnStyleModel]) -> None:
            self._inner = inner

        def predict(self, X: List[List[float]]) -> List[int]:
            return self._inner.call("predict", X)

    def main() -> None:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

        print("=" * 60)
        print("AdapterBase: TensorFlowToSklearn -> sklearn fit/predict over TF-style API")
        print("=" * 60)
        tf_model = MockTensorFlowModel()
        tf_model.compile_model(optimizer="sgd")
        adapter = TensorFlowToSklearnAdapter(tf_model)
        X_train = [[1.0, 1.0], [2.0, 0.0]]
        y_train = [1.0, 0.0]
        adapter.fit(X_train, y_train)
        X_test = [[1.0, 2.0], [0.5, 0.5]]
        preds = adapter.predict(X_test)
        print("Sklearn-style predict:", preds)

        print()
        print("=" * 60)
        print("LoggingDecorator + CachingDecorator: mock model predict")
        print("=" * 60)
        base = MockSklearnStyleModel()
        logged = LoggingDecorator(base)
        bridge = PredictMethodBridge(logged)
        cached = CachingDecorator(bridge)
        X = [[1.0, 2.0], [0.1, 0.1]]
        print("First predict (miss, runs underlying):")
        t0 = time.perf_counter()
        r1 = cached.call("predict", X)
        print("  result:", r1, f"elapsed={1000 * (time.perf_counter() - t0):.1f}ms")
        print("Second predict (cache hit, fast):")
        t1 = time.perf_counter()
        r2 = cached.call("predict", X)
        print("  result:", r2, f"elapsed={1000 * (time.perf_counter() - t1):.1f}ms")

        print()
        print("=" * 60)
        print("LazyProxy: heavy model loads on first attribute access")
        print("=" * 60)
        load_start = time.perf_counter()

        def load_heavy() -> MockSklearnStyleModel:
            time.sleep(0.15)
            print(
                f"  [heavy loader] finished after {1000 * (time.perf_counter() - load_start):.0f}ms from proxy creation"
            )
            return MockSklearnStyleModel()

        proxy: LazyProxy[MockSklearnStyleModel] = LazyProxy(load_heavy)
        print("Proxy created (no load yet):", repr(proxy))
        before = time.perf_counter()
        _ = proxy.predict([[2.0, 2.0]])
        after = time.perf_counter()
        print("First predict via proxy:", f"{1000 * (after - before):.1f}ms after first access")
        print("Proxy after load:", repr(proxy))

else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
