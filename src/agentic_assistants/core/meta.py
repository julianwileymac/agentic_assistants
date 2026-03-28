"""
Metaprogramming utilities.

Provides metaclasses and decorators for advanced class construction patterns:
Singleton, plugin auto-discovery, immutable classes, and subclass validation.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    """Thread-safe Singleton metaclass.

    Usage:
        class Config(metaclass=SingletonMeta):
            def __init__(self, value=0):
                self.value = value
    """

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

    @classmethod
    def reset(mcs, cls: type) -> None:
        """Remove the singleton instance (useful in tests)."""
        mcs._instances.pop(cls, None)


class PluginMeta(type):
    """Metaclass that auto-discovers subclasses into a registry.

    The first class using this metaclass becomes the root; all subsequent
    subclasses register themselves by name.

    Usage:
        class BasePlugin(metaclass=PluginMeta):
            pass

        class MyPlugin(BasePlugin):
            pass

        BasePlugin._plugins  # {'MyPlugin': <class 'MyPlugin'>}
    """

    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        super().__init__(name, bases, namespace)
        if not hasattr(cls, "_plugins"):
            cls._plugins: dict[str, type] = {}
        elif bases:
            cls._plugins[name] = cls


def frozen_attrs(cls: type) -> type:
    """Decorator that makes class instances immutable after __init__.

    Usage:
        @frozen_attrs
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y
    """
    original_init = cls.__init__

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        object.__setattr__(self, "_frozen", False)
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen", True)

    def frozen_setattr(self: Any, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"Cannot set attribute '{name}' on frozen instance of {type(self).__name__}"
            )
        object.__setattr__(self, name, value)

    cls.__init__ = new_init
    cls.__setattr__ = frozen_setattr
    return cls


def validate_subclass(*required_attrs: str):
    """Decorator using __init_subclass__ to ensure subclasses define required attributes.

    Usage:
        @validate_subclass("name", "version")
        class BasePlugin:
            name: str
            version: str

        class GoodPlugin(BasePlugin):
            name = "my-plugin"
            version = "1.0"

        class BadPlugin(BasePlugin):  # raises TypeError
            pass
    """

    def decorator(cls: type) -> type:
        original_init_subclass = cls.__init_subclass__

        def new_init_subclass(subcls: type, **kwargs: Any) -> None:
            original_init_subclass(**kwargs)
            for attr in required_attrs:
                if not hasattr(subcls, attr) or getattr(subcls, attr) is None:
                    raise TypeError(
                        f"{subcls.__name__} must define '{attr}' "
                        f"(required by {cls.__name__})"
                    )

        cls.__init_subclass__ = classmethod(new_init_subclass)
        return cls

    return decorator


__all__ = [
    "SingletonMeta",
    "PluginMeta",
    "frozen_attrs",
    "validate_subclass",
]
