# requires: (no external deps - uses core package only)

"""ML-oriented creational patterns: ModelFactory, PipelineBuilder, and Singleton (SingletonMeta)."""

from __future__ import annotations

import logging
from typing import Any

try:
    from agentic_assistants.core.meta import SingletonMeta
    from agentic_assistants.core.patterns import ModelFactory, PipelineBuilder
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class LinearModel:
        def __init__(self) -> None:
            self.kind = "linear"

        def __repr__(self) -> str:
            return "LinearModel()"

    class TreeModel:
        def __init__(self) -> None:
            self.kind = "tree"

        def __repr__(self) -> str:
            return "TreeModel()"

    class NeuralModel:
        def __init__(self) -> None:
            self.kind = "neural"

        def __repr__(self) -> str:
            return "NeuralModel()"

    class GlobalMLConfig(metaclass=SingletonMeta):
        """Thread-safe singleton for global ML run settings (Singleton pattern via SingletonMeta)."""

        def __init__(self, seed: int = 42, experiment: str = "default") -> None:
            self.seed = seed
            self.experiment = experiment

        def __repr__(self) -> str:
            return f"GlobalMLConfig(seed={self.seed}, experiment={self.experiment!r})"

    def main() -> None:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

        print("=" * 60)
        print("ModelFactory: register constructors, create instances dynamically")
        print("=" * 60)
        factory: ModelFactory[Any] = ModelFactory()
        factory.register("linear", LinearModel)
        factory.register("tree", TreeModel)
        factory.register("neural", NeuralModel)

        print("Registered model types:", factory.list_registered())
        for name in ("linear", "tree", "neural"):
            model = factory.create(name)
            print(f"  factory.create({name!r}) -> {model!r}")

        print()
        print("=" * 60)
        print("PipelineBuilder: load -> preprocess -> feature_engineer -> train -> evaluate")
        print("=" * 60)

        def load(_: Any = None) -> dict[str, Any]:
            return {"raw": [[1, 2], [3, 4], [5, 6]]}

        def preprocess(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "scaled": [[x / 10 for x in row] for row in state["raw"]]}

        def feature_engineer(state: dict[str, Any]) -> dict[str, Any]:
            feats = [sum(row) for row in state["scaled"]]
            return {**state, "features": feats}

        def train(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "weights": [0.1, 0.2], "train_loss": 0.35}

        def evaluate(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "val_accuracy": 0.87}

        pipeline = (
            PipelineBuilder()
            .configure("dataset", "demo")
            .add_step("load", load)
            .add_step("preprocess", preprocess)
            .add_step("feature_engineer", feature_engineer)
            .add_step("train", train)
            .add_step("evaluate", evaluate)
        )
        built = pipeline.build()
        print("Pipeline config: {'dataset': 'demo'}  # set via .configure('dataset', 'demo')")
        print("Pipeline steps (name, callable):")
        for name, _fn in built:
            print(f"  - {name}")
        final_state = pipeline.run()
        print("Final pipeline state keys:", sorted(final_state.keys()))
        print("val_accuracy:", final_state.get("val_accuracy"))

        print()
        print("=" * 60)
        print("Singleton (SingletonMeta): one global config instance")
        print("=" * 60)
        SingletonMeta.reset(GlobalMLConfig)
        a = GlobalMLConfig(seed=7, experiment="run-a")
        b = GlobalMLConfig(seed=99, experiment="ignored")
        print("First construction: ", repr(a))
        print("Second construction:", repr(b))
        print("Same object?", a is b)
        print("Effective seed/experiment (second ctor ignored):", a.seed, a.experiment)

else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
