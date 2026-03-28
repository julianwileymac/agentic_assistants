"""
Unified observability facade wrapping Logfire, OpenTelemetry, or console logging.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Literal, Optional

from agentic_assistants.config import AgenticConfig

logger = logging.getLogger(__name__)

BackendType = Literal["auto", "logfire", "otel", "console"]


class ObservabilityManager:
    """Facade over Logfire, OpenTelemetry, and console-based observability."""

    _instance: Optional[ObservabilityManager] = None

    def __init__(self, backend: BackendType = "auto", config: Optional[AgenticConfig] = None) -> None:
        self._backend = backend
        self._config = config or AgenticConfig()
        self._configured = False
        self._logfire: Any = None
        self._telemetry: Any = None

    @classmethod
    def configure(
        cls,
        backend: BackendType = "auto",
        *,
        config: Optional[AgenticConfig] = None,
        **kwargs: Any,
    ) -> ObservabilityManager:
        instance = cls(backend=backend, config=config)
        instance._setup(backend, **kwargs)
        cls._instance = instance
        return instance

    @classmethod
    def get_instance(cls) -> ObservabilityManager:
        if cls._instance is None:
            cls._instance = cls(backend="auto")
            cls._instance._setup("auto")
        return cls._instance

    def _setup(self, backend: BackendType, **kwargs: Any) -> None:
        if backend == "auto":
            self._setup_auto(**kwargs)
        elif backend == "logfire":
            self._setup_logfire(**kwargs)
        elif backend == "otel":
            self._setup_otel(**kwargs)
        else:
            self._setup_console(**kwargs)
        self._configured = True
        logger.info("Observability configured with backend=%s", self._backend)

    def _setup_auto(self, **kwargs: Any) -> None:
        try:
            import logfire  # noqa: F401

            self._setup_logfire(**kwargs)
            return
        except Exception:
            pass

        if self._config.telemetry_enabled:
            self._setup_otel(**kwargs)
        else:
            self._setup_console(**kwargs)

    def _setup_logfire(self, **kwargs: Any) -> None:
        try:
            import logfire

            logfire.configure(**kwargs)
            self._logfire = logfire
            self._backend = "logfire"
        except ImportError:
            logger.warning("logfire is not installed; falling back to OpenTelemetry/console")
            if self._config.telemetry_enabled:
                self._setup_otel(**kwargs)
            else:
                self._setup_console(**kwargs)

    def _setup_otel(self, **kwargs: Any) -> None:
        try:
            from agentic_assistants.core.telemetry import TelemetryManager

            self._telemetry = TelemetryManager(self._config)
            self._telemetry.initialize()
            self._backend = "otel"
        except Exception as exc:
            logger.warning("OpenTelemetry setup failed (%s). Falling back to console.", exc)
            self._setup_console(**kwargs)

    def _setup_console(self, **kwargs: Any) -> None:
        self._backend = "console"

    @contextmanager
    def span(self, name: str, **attributes: Any):
        """Create an execution span with the selected backend."""
        if self._backend == "logfire" and self._logfire is not None:
            with self._logfire.span(name, **attributes) as span_obj:
                yield span_obj
            return

        if self._backend == "otel" and self._telemetry is not None:
            with self._telemetry.span(name, attributes=attributes) as span_obj:
                yield span_obj
            return

        start = time.perf_counter()
        yield None
        elapsed = time.perf_counter() - start
        logger.info("[span] %s (%.3fs) %s", name, elapsed, attributes or "")

    def log(self, message: str, level: str = "info", **kwargs: Any) -> None:
        if self._backend == "logfire" and self._logfire is not None:
            log_fn = getattr(self._logfire, level, self._logfire.info)
            log_fn(message, **kwargs)
            return
        log_fn = getattr(logger, level, logger.info)
        if kwargs:
            log_fn("%s | %s", message, kwargs)
        else:
            log_fn(message)

    def metric(self, name: str, value: float, **attributes: Any) -> None:
        if self._backend == "otel" and self._telemetry is not None:
            self._telemetry.record_agent_metrics(
                agent_name=attributes.get("agent_name", "unknown"),
                model=attributes.get("model", "unknown"),
                duration_seconds=attributes.get("duration_seconds", 0.0),
                tokens_input=attributes.get("tokens_input", 0),
                tokens_output=attributes.get("tokens_output", 0),
                success=attributes.get("success", True),
            )
            return
        logger.info("[metric] %s=%s %s", name, value, attributes or "")

    def instrument_pydantic(self) -> None:
        if self._logfire is not None:
            try:
                self._logfire.instrument_pydantic()
            except Exception as exc:
                logger.debug("Could not instrument pydantic: %s", exc)

    def instrument_httpx(self) -> None:
        if self._logfire is not None:
            try:
                self._logfire.instrument_httpx()
            except Exception as exc:
                logger.debug("Could not instrument httpx: %s", exc)

    def instrument_fastapi(self, app: Any) -> None:
        if self._logfire is not None:
            try:
                self._logfire.instrument_fastapi(app)
            except Exception as exc:
                logger.debug("Could not instrument fastapi: %s", exc)

    def instrument_sqlalchemy(self, engine: Any) -> None:
        if self._logfire is not None:
            try:
                self._logfire.instrument_sqlalchemy(engine=engine)
            except Exception as exc:
                logger.debug("Could not instrument sqlalchemy: %s", exc)


__all__ = [
    "BackendType",
    "ObservabilityManager",
]

