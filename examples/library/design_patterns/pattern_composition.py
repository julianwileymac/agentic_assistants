# requires: (no external deps - uses core package only)

"""Composing creational, structural, and behavioral patterns for an ML-style workflow."""

from __future__ import annotations

import logging
from typing import Any, Callable, List

try:
    from agentic_assistants.core.patterns import (
        Command,
        CommandQueue,
        EventBus,
        LoggingDecorator,
        ModelFactory,
        PipelineBuilder,
        StrategyContext,
    )
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class RequirementAwareModel:
        """Tiny pluggable model object selected by factory + strategy."""

        def __init__(self, label: str) -> None:
            self.label = label

        def fit(self, X: List[List[float]], y: List[float] | None = None) -> None:
            pass

        def predict(self, X: List[List[float]]) -> List[float]:
            if self.label == "linear":
                return [row[0] * 0.5 + row[1] * 0.5 for row in X]
            if self.label == "tree":
                return [1.0 if row[0] > 0.5 else 0.0 for row in X]
            return [float(sum(row)) / max(len(row), 1) for row in X]

    class _StepFn:
        """Callable object with a named method so LoggingDecorator can wrap it."""

        def __init__(self, name: str, fn: Callable[[Any], Any]) -> None:
            self._name = name
            self._fn = fn

        def run(self, state: Any) -> Any:
            return self._fn(state)

    class LoggedPipelineCommand(Command):
        """Command that runs a PipelineBuilder and stores result for printing."""

        def __init__(self, pipeline: PipelineBuilder[Any], initial: Any) -> None:
            self._pipeline = pipeline
            self._initial = initial
            self._result: Any = None

        def execute(self) -> Any:
            self._result = self._pipeline.run(self._initial)
            return self._result

        def undo(self) -> None:
            self._result = None

    class MonitoredCommandQueue(CommandQueue):
        """CommandQueue subclass: Observer (EventBus) logs each command execution."""

        def __init__(self, bus: EventBus) -> None:
            super().__init__()
            self._bus = bus

        def execute_all(self) -> list[Any]:
            results: list[Any] = []
            while self._pending:
                cmd = self._pending.pop(0)
                name = type(cmd).__name__
                self._bus.publish("command_started", name)
                out = cmd.execute()
                results.append(out)
                self._executed.append(cmd)
                self._bus.publish("command_finished", name, out)
            return results

    def pick_model_name(requirements: dict[str, Any]) -> str:
        if requirements.get("interpretability"):
            return "linear"
        if requirements.get("tabular_deep"):
            return "neural"
        return "tree"

    def main() -> None:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

        print("=" * 60)
        print("Factory + Strategy: ModelFactory + StrategyContext from requirements")
        print("=" * 60)
        factory: ModelFactory[RequirementAwareModel] = ModelFactory()
        factory.register("linear", lambda: RequirementAwareModel("linear"))
        factory.register("tree", lambda: RequirementAwareModel("tree"))
        factory.register("neural", lambda: RequirementAwareModel("neural"))

        ctx: StrategyContext[RequirementAwareModel] = StrategyContext()
        for req in (
            {"interpretability": True},
            {"speed": True},
            {"tabular_deep": True},
        ):
            name = pick_model_name(req)
            model = factory.create(name)
            ctx.set_strategy(model)
            ctx.execute("fit", [[0.4, 0.6], [0.1, 0.9]], [0.0, 1.0])
            preds = ctx.execute("predict", [[0.5, 0.5]])
            print(f"  requirements={req} -> model={name!r} predict[0]={preds[0]:.4f}")

        print()
        print("=" * 60)
        print("Observer + Command: EventBus monitors MonitoredCommandQueue execution")
        print("=" * 60)
        bus = EventBus()
        log: list[str] = []

        def on_started(cmd_name: str) -> None:
            log.append(f"start:{cmd_name}")
            print(f"  event: command_started {cmd_name}")

        def on_finished(cmd_name: str, result: Any) -> None:
            log.append(f"finish:{cmd_name}")
            detail = (
                list(result.keys()) if isinstance(result, dict) else type(result).__name__
            )
            print(f"  event: command_finished {cmd_name} -> {detail}")

        bus.subscribe("command_started", on_started)
        bus.subscribe("command_finished", on_finished)

        obs_queue = MonitoredCommandQueue(bus)
        mini_pipe = PipelineBuilder().add_step("noop", lambda s: s)
        obs_queue.add(LoggedPipelineCommand(mini_pipe, {"seed": 1}))
        obs_queue.execute_all()
        print("  Event log:", log)

        print()
        print("=" * 60)
        print("Builder + Decorator: PipelineBuilder with LoggingDecorator per step")
        print("=" * 60)

        def load(state: Any = None) -> dict[str, Any]:
            _ = state
            return {"rows": [[1, 2], [3, 4]]}

        def preprocess(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "mean_row": [sum(r) / len(r) for r in state["rows"]]}

        def train(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "loss": 0.42}

        def evaluate(state: dict[str, Any]) -> dict[str, Any]:
            return {**state, "metric": 0.91}

        def wrap_logged_step(step_name: str, fn: Callable[[Any], Any]) -> Callable[..., Any]:
            holder = _StepFn(step_name, fn)
            dec = LoggingDecorator(holder)

            def wrapped(state: Any = None) -> Any:
                return dec.call("run", state)

            return wrapped

        builder = PipelineBuilder()
        for step_name, fn in (
            ("load", load),
            ("preprocess", preprocess),
            ("train", train),
            ("evaluate", evaluate),
        ):
            builder.add_step(step_name, wrap_logged_step(step_name, fn))

        final = builder.run(None)
        print("Composed pipeline output:", final)

else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
