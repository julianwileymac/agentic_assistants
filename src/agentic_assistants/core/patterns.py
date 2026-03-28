"""
Gang-of-Four design pattern primitives for ML platforms.

Provides reusable building blocks for Creational, Structural, and Behavioral
patterns as described in the "Software Design Patterns for Machine Learning
Platforms" section. Each class is intentionally minimal so that downstream
code can compose and extend them.

Usage:
    >>> factory = ModelFactory()
    >>> factory.register("linear", lambda: "LinearRegression()")
    >>> factory.create("linear")
    'LinearRegression()'
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import pickle
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, runtime_checkable

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


# ---------------------------------------------------------------------------
# Creational Patterns
# ---------------------------------------------------------------------------


class ModelFactory(Generic[T]):
    """Dynamic model/algorithm instantiation via registered constructors."""

    def __init__(self) -> None:
        self._constructors: dict[str, Callable[..., T]] = {}

    def register(self, name: str, constructor: Callable[..., T]) -> None:
        self._constructors[name] = constructor
        logger.debug("Factory registered '%s'", name)

    def create(self, name: str, *args: Any, **kwargs: Any) -> T:
        ctor = self._constructors.get(name)
        if ctor is None:
            raise KeyError(f"Unknown model type: {name}. Registered: {list(self._constructors)}")
        return ctor(*args, **kwargs)

    def list_registered(self) -> list[str]:
        return list(self._constructors.keys())


class Pipeline:
    """Callable pipeline returned by ``PipelineBuilder.build()``."""

    def __init__(
        self,
        steps: list[tuple[str, Callable[..., Any]]],
        config: dict[str, Any],
    ) -> None:
        self.steps = steps
        self.config = config

    def run(self, initial: Any = None) -> Any:
        state = initial
        for name, fn in self.steps:
            logger.debug("Pipeline step: %s", name)
            state = fn(state) if state is not None else fn()
        return state

    async def async_run(self, initial: Any = None) -> Any:
        state = initial
        for name, fn in self.steps:
            logger.debug("Pipeline step (async): %s", name)
            if asyncio.iscoroutinefunction(fn):
                state = await fn(state) if state is not None else await fn()
            else:
                state = fn(state) if state is not None else fn()
        return state

    def __call__(self, initial: Any = None) -> Any:
        return self.run(initial)

    def __len__(self) -> int:
        return len(self.steps)

    def __repr__(self) -> str:
        names = [n for n, _ in self.steps]
        return f"Pipeline({names})"


class PipelineBuilder(Generic[T]):
    """Fluent builder for multi-stage pipelines.

    Each step is a callable that transforms the accumulated state.
    """

    def __init__(self) -> None:
        self._steps: list[tuple[str, Callable[..., Any]]] = []
        self._config: dict[str, Any] = {}

    def add_step(self, name: str, fn: Callable[..., Any]) -> "PipelineBuilder[T]":
        self._steps.append((name, fn))
        return self

    def configure(self, key: str, value: Any) -> "PipelineBuilder[T]":
        self._config[key] = value
        return self

    def build(self) -> Pipeline:
        return Pipeline(list(self._steps), dict(self._config))

    def run(self, initial: Any = None) -> Any:
        return self.build().run(initial)

    def reset(self) -> "PipelineBuilder[T]":
        self._steps.clear()
        self._config.clear()
        return self


# ---------------------------------------------------------------------------
# Structural Patterns
# ---------------------------------------------------------------------------


class AdapterBase(ABC, Generic[T, R]):
    """Converts interface T into interface R."""

    def __init__(self, adaptee: T) -> None:
        self._adaptee = adaptee

    @abstractmethod
    def adapt(self, *args: Any, **kwargs: Any) -> R:
        """Transform the adaptee's output into the target interface."""

    @property
    def adaptee(self) -> T:
        return self._adaptee


class DecoratorBase(Generic[T]):
    """Wraps an object and adds behaviour without modifying its implementation.

    Subclasses override ``_before``, ``_after``, or ``_on_error`` hooks.
    """

    def __init__(self, wrapped: T) -> None:
        self._wrapped = wrapped

    @property
    def wrapped(self) -> T:
        return self._wrapped

    def _before(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Hook called before the wrapped method."""

    def _after(self, method_name: str, result: Any) -> Any:
        """Hook called after the wrapped method. Return value replaces result if not None."""
        return result

    def _on_error(self, method_name: str, exc: Exception) -> None:
        """Hook called if the wrapped method raises."""

    def call(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        self._before(method_name, *args, **kwargs)
        try:
            fn = getattr(self._wrapped, method_name)
            result = fn(*args, **kwargs)
        except Exception as exc:
            self._on_error(method_name, exc)
            raise
        return self._after(method_name, result)


class LazyProxy(Generic[T]):
    """Defers creation of a heavy object until first attribute access."""

    def __init__(self, factory: Callable[[], T]) -> None:
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_instance", None)
        object.__setattr__(self, "_lock", threading.Lock())

    def _get_instance(self) -> T:
        if object.__getattribute__(self, "_instance") is None:
            lock = object.__getattribute__(self, "_lock")
            with lock:
                if object.__getattribute__(self, "_instance") is None:
                    factory = object.__getattribute__(self, "_factory")
                    object.__setattr__(self, "_instance", factory())
        return object.__getattribute__(self, "_instance")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_instance(), name)

    def __repr__(self) -> str:
        inst = object.__getattribute__(self, "_instance")
        if inst is None:
            return "<LazyProxy(not loaded)>"
        return f"<LazyProxy({inst!r})>"


class ProxyBase(ABC, Generic[T]):
    """Abstract proxy that intercepts access to a wrapped subject.

    Useful for prediction caching, access control, or lazy loading.
    """

    def __init__(self, subject: T) -> None:
        self._subject = subject

    @property
    def subject(self) -> T:
        return self._subject

    @abstractmethod
    def intercept(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Called instead of direct method access on the subject."""

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._subject, name)
        if callable(attr):
            def proxy_call(*a: Any, **kw: Any) -> Any:
                return self.intercept(name, *a, **kw)
            return proxy_call
        return attr


class CachingProxy(ProxyBase[T]):
    """Caches return values of method calls on the wrapped subject."""

    def __init__(self, subject: T, maxsize: int = 256) -> None:
        super().__init__(subject)
        self._cache: dict[str, Any] = {}
        self._maxsize = maxsize

    def intercept(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        key = self._make_key(method_name, args, kwargs)
        if key in self._cache:
            return self._cache[key]
        fn = getattr(self._subject, method_name)
        result = fn(*args, **kwargs)
        if len(self._cache) >= self._maxsize:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = result
        return result

    @staticmethod
    def _make_key(method: str, args: tuple, kwargs: dict) -> str:
        try:
            raw = pickle.dumps((method, args, sorted(kwargs.items())))
            return hashlib.sha256(raw).hexdigest()
        except (pickle.PicklingError, TypeError):
            return f"{method}:{args}:{sorted(kwargs.items())}"


class LoggingDecorator(DecoratorBase[T]):
    """Concrete decorator that logs method calls with timing."""

    def _before(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        logger.info("Calling %s", method_name)
        object.__setattr__(self, "_call_start", time.perf_counter())

    def _after(self, method_name: str, result: Any) -> Any:
        start = getattr(self, "_call_start", time.perf_counter())
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("%s completed in %.1fms", method_name, elapsed)
        return result


class CachingDecorator(DecoratorBase[T]):
    """Concrete decorator that caches method results using hash-based keys."""

    def __init__(self, wrapped: T) -> None:
        super().__init__(wrapped)
        self._cache: dict[str, Any] = {}

    def call(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        key = self._make_key(method_name, args, kwargs)
        if key in self._cache:
            return self._cache[key]
        result = super().call(method_name, *args, **kwargs)
        self._cache[key] = result
        return result

    @staticmethod
    def _make_key(method: str, args: tuple, kwargs: dict) -> str:
        try:
            raw = pickle.dumps((method, args, sorted(kwargs.items())))
            return hashlib.sha256(raw).hexdigest()
        except (pickle.PicklingError, TypeError):
            return f"{method}:{args}:{sorted(kwargs.items())}"


# ---------------------------------------------------------------------------
# Behavioral Patterns
# ---------------------------------------------------------------------------


@runtime_checkable
class AlgorithmStrategy(Protocol):
    """Swappable fit/predict interface for ML models."""

    def fit(self, X: Any, y: Any = None) -> None: ...

    def predict(self, X: Any) -> Any: ...


class StrategyContext(Generic[T]):
    """Holds a strategy and delegates to it. Allows runtime swapping."""

    def __init__(self, strategy: T | None = None) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> T | None:
        return self._strategy

    def set_strategy(self, strategy: T) -> None:
        self._strategy = strategy

    def execute(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        if self._strategy is None:
            raise RuntimeError("No strategy set")
        fn = getattr(self._strategy, method_name)
        return fn(*args, **kwargs)


class Observer(ABC):
    """Base class for observers in the Observer pattern."""

    @abstractmethod
    def update(self, event: str, data: Any = None) -> None:
        """Receive a notification from the subject."""


class Subject:
    """Observable subject that notifies registered observers of state changes."""

    def __init__(self) -> None:
        self._observers: dict[str, list[Observer]] = defaultdict(list)

    def attach(self, event: str, observer: Observer) -> None:
        if observer not in self._observers[event]:
            self._observers[event].append(observer)

    def detach(self, event: str, observer: Observer) -> None:
        observers = self._observers.get(event, [])
        if observer in observers:
            observers.remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        for observer in self._observers.get(event, []):
            try:
                observer.update(event, data)
            except Exception:
                logger.exception("Observer %s failed for '%s'", observer, event)


class EventBus:
    """Simple pub/sub event system for Observer pattern."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable[..., Any]) -> None:
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., Any]) -> None:
        subs = self._subscribers.get(event, [])
        if callback in subs:
            subs.remove(callback)

    def publish(self, event: str, *args: Any, **kwargs: Any) -> None:
        for callback in self._subscribers.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                logger.exception("Event handler failed for '%s'", event)

    def clear(self, event: Optional[str] = None) -> None:
        if event:
            self._subscribers.pop(event, None)
        else:
            self._subscribers.clear()


class Command(ABC):
    """Encapsulated operation with optional undo support."""

    @abstractmethod
    def execute(self) -> Any:
        """Run the command."""

    def undo(self) -> None:
        """Reverse the command. Override if the operation is reversible."""
        raise NotImplementedError(f"{type(self).__name__} does not support undo")


class CommandQueue:
    """Queues commands for sequential execution with rollback capability."""

    def __init__(self) -> None:
        self._pending: list[Command] = []
        self._executed: list[Command] = []

    def add(self, command: Command) -> None:
        self._pending.append(command)

    def execute_all(self) -> list[Any]:
        results: list[Any] = []
        while self._pending:
            cmd = self._pending.pop(0)
            results.append(cmd.execute())
            self._executed.append(cmd)
        return results

    def rollback(self) -> int:
        rolled = 0
        while self._executed:
            cmd = self._executed.pop()
            try:
                cmd.undo()
                rolled += 1
            except NotImplementedError:
                logger.warning("Cannot undo %s", type(cmd).__name__)
        return rolled

    def clear(self) -> None:
        self._pending.clear()
        self._executed.clear()


__all__ = [
    "ModelFactory",
    "Pipeline",
    "PipelineBuilder",
    "AdapterBase",
    "DecoratorBase",
    "LazyProxy",
    "ProxyBase",
    "CachingProxy",
    "LoggingDecorator",
    "CachingDecorator",
    "AlgorithmStrategy",
    "StrategyContext",
    "Observer",
    "Subject",
    "EventBus",
    "Command",
    "CommandQueue",
]
