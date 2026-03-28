# requires: (no external deps - uses core package only)

"""ML-oriented behavioral patterns: Strategy, EventBus (Observer), Command + CommandQueue."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, List

try:
    from agentic_assistants.core.patterns import (
        Command,
        CommandQueue,
        EventBus,
        StrategyContext,
    )
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class LinearStrategy:
        def fit(self, X: List[List[float]], y: List[float] | None = None) -> None:
            self._coef = [0.5, 0.5]

        def predict(self, X: List[List[float]]) -> List[float]:
            return [sum(x[i] * self._coef[i] for i in range(2)) for x in X]

    class TreeStrategy:
        def fit(self, X: List[List[float]], y: List[float] | None = None) -> None:
            self._threshold = 1.0

        def predict(self, X: List[List[float]]) -> List[int]:
            return [1 if x[0] + x[1] > self._threshold else 0 for x in X]

    @dataclass
    class TrainState:
        epoch: int = 0
        loss: float = 1.0
        best_loss: float = float("inf")
        log: List[str] = field(default_factory=list)

    class TrainCommand(Command):
        def __init__(self, state: TrainState) -> None:
            self._state = state
            self._prev_epoch: int | None = None

        def execute(self) -> str:
            self._prev_epoch = self._state.epoch
            self._state.epoch += 1
            self._state.loss *= 0.9
            msg = f"train epoch={self._state.epoch} loss={self._state.loss:.4f}"
            self._state.log.append(msg)
            return msg

        def undo(self) -> None:
            if self._prev_epoch is not None:
                self._state.epoch = self._prev_epoch
            self._state.loss /= 0.9
            if self._state.log:
                self._state.log.pop()

    class EvaluateCommand(Command):
        def __init__(self, state: TrainState) -> None:
            self._state = state

        def execute(self) -> str:
            msg = f"evaluate epoch={self._state.epoch} loss={self._state.loss:.4f}"
            self._state.log.append(msg)
            return msg

        def undo(self) -> None:
            if self._state.log:
                self._state.log.pop()

    @dataclass
    class DeployState:
        deployed: bool = False
        version: str = ""

    class DeployCommand(Command):
        def __init__(self, deploy: DeployState, version: str) -> None:
            self._deploy = deploy
            self._version = version
            self._previous_version: str = ""

        def execute(self) -> str:
            self._previous_version = self._deploy.version
            self._deploy.deployed = True
            self._deploy.version = self._version
            return f"deployed v{self._version}"

        def undo(self) -> None:
            self._deploy.version = self._previous_version
            self._deploy.deployed = bool(self._previous_version)

    def main() -> None:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

        print("=" * 60)
        print("AlgorithmStrategy + StrategyContext: swap Linear vs Tree at runtime")
        print("=" * 60)
        ctx: StrategyContext[Any] = StrategyContext()
        X = [[0.2, 0.3], [2.0, 2.0]]
        ctx.set_strategy(LinearStrategy())
        ctx.execute("fit", X, [0.0, 1.0])
        print("Linear predict:", ctx.execute("predict", X))
        ctx.set_strategy(TreeStrategy())
        ctx.execute("fit", X, [0.0, 1.0])
        print("Tree predict:", ctx.execute("predict", X))

        print()
        print("=" * 60)
        print("EventBus: training lifecycle (epoch_end, loss_improved, training_complete)")
        print("=" * 60)
        bus = EventBus()
        events_fired: list[str] = []

        def on_epoch_end(epoch: int, loss: float) -> None:
            events_fired.append(f"epoch_end:{epoch}:{loss:.4f}")
            print(f"  subscriber: epoch_end epoch={epoch} loss={loss:.4f}")

        def on_loss_improved(best: float) -> None:
            events_fired.append(f"loss_improved:{best:.4f}")
            print(f"  subscriber: loss_improved best={best:.4f}")

        def on_training_complete(epochs: int) -> None:
            events_fired.append(f"training_complete:{epochs}")
            print(f"  subscriber: training_complete epochs={epochs}")

        bus.subscribe("epoch_end", on_epoch_end)
        bus.subscribe("loss_improved", on_loss_improved)
        bus.subscribe("training_complete", on_training_complete)

        best = float("inf")
        for epoch in range(1, 4):
            loss = 1.0 / epoch
            bus.publish("epoch_end", epoch, loss)
            if loss < best:
                best = loss
                bus.publish("loss_improved", best)
        bus.publish("training_complete", 3)
        print("Recorded events:", events_fired)

        print()
        print("=" * 60)
        print("Command + CommandQueue: Train, Evaluate, Deploy with undo rollback")
        print("=" * 60)
        train_state = TrainState()
        deploy_state = DeployState()
        queue = CommandQueue()
        queue.add(TrainCommand(train_state))
        queue.add(EvaluateCommand(train_state))
        queue.add(TrainCommand(train_state))
        queue.add(EvaluateCommand(train_state))
        queue.add(DeployCommand(deploy_state, "1.0.0"))

        results = queue.execute_all()
        print("Execute results:", results)
        print("Train log:", train_state.log)
        print("Deploy state:", deploy_state)

        rolled = queue.rollback()
        print(f"Rollback reversed {rolled} command(s)")
        print("After rollback deploy state:", deploy_state)
        print(
            "Train state after rollback: epoch=",
            train_state.epoch,
            "loss=",
            round(train_state.loss, 6),
        )

else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
