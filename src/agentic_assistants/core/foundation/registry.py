"""
Auto-registration primitives using __init_subclass__.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, ClassVar, Optional

logger = logging.getLogger(__name__)


class AutoRegistry:
    """Base class that auto-registers subclasses and metadata."""

    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init_subclass__(
        cls,
        register: bool = True,
        registry_key: Optional[str] = None,
        registry_metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if register:
            key = registry_key or cls.__name__
            cls.register_class(key, cls, metadata=registry_metadata)

    @classmethod
    def register_class(
        cls,
        key: str,
        klass: type,
        *,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        with cls._lock:
            if key in cls._registry and cls._registry[key] is not klass:
                logger.warning(
                    "Registry key '%s' already mapped to %s, overwriting with %s",
                    key,
                    cls._registry[key].__qualname__,
                    klass.__qualname__,
                )
            cls._registry[key] = klass
            if metadata is not None:
                cls._registry_meta[key] = dict(metadata)
        logger.debug("Registered %s as '%s'", klass.__qualname__, key)

    @classmethod
    def unregister(cls, key: str) -> None:
        with cls._lock:
            cls._registry.pop(key, None)
            cls._registry_meta.pop(key, None)

    @classmethod
    def get(cls, name: str) -> type:
        try:
            return cls._registry[name]
        except KeyError as exc:
            available = ", ".join(sorted(cls._registry))
            raise KeyError(f"'{name}' is not registered. Available: [{available}]") from exc

    @classmethod
    def create(cls, name: str, *args: Any, **kwargs: Any) -> Any:
        klass = cls.get(name)
        return klass(*args, **kwargs)

    @classmethod
    def get_or_none(cls, name: str) -> Optional[type]:
        return cls._registry.get(name)

    @classmethod
    def get_metadata(cls, name: str) -> dict[str, Any]:
        return dict(cls._registry_meta.get(name, {}))

    @classmethod
    def list_registered(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def list_items(cls) -> list[tuple[str, type]]:
        return sorted(cls._registry.items(), key=lambda item: item[0])

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._registry

    @classmethod
    def clear_registry(cls) -> None:
        with cls._lock:
            cls._registry.clear()
            cls._registry_meta.clear()


class ProviderRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


class AdapterRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


class PatternRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


class DataSourceTypeRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


class SerializerRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


class NodeTypeRegistry(AutoRegistry):
    _registry: ClassVar[dict[str, type]] = {}
    _registry_meta: ClassVar[dict[str, dict[str, Any]]] = {}


__all__ = [
    "AutoRegistry",
    "ProviderRegistry",
    "AdapterRegistry",
    "PatternRegistry",
    "DataSourceTypeRegistry",
    "SerializerRegistry",
    "NodeTypeRegistry",
]

