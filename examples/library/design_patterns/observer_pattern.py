# requires: agentic-assistants

"""Observer pattern: training Subject with metric monitors, dashboard, and threshold alerts."""

from __future__ import annotations

from typing import Any

try:
    from agentic_assistants.core.patterns import Observer, Subject
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class TrainingMonitor(Observer):
        """Records epoch-level metrics from training notifications."""

        def __init__(self) -> None:
            self.history: list[dict[str, Any]] = []

        def update(self, event: str, data: Any = None) -> None:
            if event != "epoch_end" or not isinstance(data, dict):
                return
            self.history.append(dict(data))

    class DashboardNotifier(Observer):
        """Formats epoch updates for a simple console dashboard."""

        def update(self, event: str, data: Any = None) -> None:
            if event != "epoch_end" or not isinstance(data, dict):
                return
            epoch = data.get("epoch", "?")
            loss = data.get("loss", 0.0)
            acc = data.get("accuracy", 0.0)
            print(f"  [dashboard] epoch={epoch} loss={loss:.4f} accuracy={acc:.3f}")

    class AlertObserver(Observer):
        """Raises console warnings when metrics breach configured thresholds."""

        def __init__(self, *, max_loss: float = 0.5, min_accuracy: float = 0.85) -> None:
            self.max_loss = max_loss
            self.min_accuracy = min_accuracy
            self.alerts: list[str] = []

        def update(self, event: str, data: Any = None) -> None:
            if event != "epoch_end" or not isinstance(data, dict):
                return
            loss = float(data.get("loss", 0.0))
            acc = float(data.get("accuracy", 1.0))
            if loss > self.max_loss:
                msg = f"LOSS ALERT: loss {loss:.4f} > {self.max_loss}"
                self.alerts.append(msg)
                print(f"  *** {msg}")
            if acc < self.min_accuracy:
                msg = f"ACCURACY ALERT: accuracy {acc:.3f} < {self.min_accuracy}"
                self.alerts.append(msg)
                print(f"  *** {msg}")

    def main() -> None:
        print("Observer pattern: Subject notifies TrainingMonitor, DashboardNotifier, AlertObserver")
        print("-" * 60)

        subject = Subject()
        monitor = TrainingMonitor()
        dashboard = DashboardNotifier()
        alerts = AlertObserver(max_loss=0.55, min_accuracy=0.82)

        subject.attach("epoch_end", monitor)
        subject.attach("epoch_end", dashboard)
        subject.attach("epoch_end", alerts)

        # Synthetic training loop (no real model)
        print("Simulated training loop:")
        for epoch in range(1, 6):
            loss = max(0.05, 0.7 - epoch * 0.12 + (0.03 if epoch == 2 else 0))
            accuracy = min(0.97, 0.55 + epoch * 0.08)
            subject.notify(
                "epoch_end",
                {"epoch": epoch, "loss": loss, "accuracy": accuracy},
            )

        print()
        print("TrainingMonitor captured epochs:", len(monitor.history))
        if monitor.history:
            last = monitor.history[-1]
            print(f"  last epoch snapshot: {last}")
        print("AlertObserver raised", len(alerts.alerts), "warning(s).")


else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
