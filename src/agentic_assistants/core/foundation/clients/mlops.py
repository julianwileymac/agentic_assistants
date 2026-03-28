"""
Typed MLOps client facades.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker


class MLFlowClient:
    """Thin typed facade over MLFlowTracker for reusable core workflows."""

    def __init__(self, config: Optional[AgenticConfig] = None) -> None:
        self.config = config or AgenticConfig()
        self.tracker = MLFlowTracker(self.config)

    @contextmanager
    def run(self, run_name: str, tags: Optional[dict[str, str]] = None) -> Iterator[Any]:
        with self.tracker.start_run(run_name=run_name, tags=tags or {}):
            yield self.tracker

    def log_params(self, params: dict[str, Any]) -> None:
        self.tracker.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.tracker.log_metrics(metrics)

    def log_text(self, text: str, artifact_path: str) -> None:
        self.tracker.log_text(text, artifact_path)


class PrefectClient:
    """Optional Prefect facade with import-safe capability detection."""

    def __init__(self) -> None:
        self._prefect: Any = None
        try:
            import prefect

            self._prefect = prefect
        except Exception:
            self._prefect = None

    @property
    def available(self) -> bool:
        return self._prefect is not None

    def require_available(self) -> None:
        if not self.available:
            raise RuntimeError(
                "Prefect is not installed. Install optional extras that include `prefect`."
            )

    def build_flow(self, fn: Any, *, name: Optional[str] = None) -> Any:
        self.require_available()
        return self._prefect.flow(name=name)(fn)

