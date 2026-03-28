# requires: agentic-assistants

"""Proxy pattern: lazy model load, prediction caching, and permission-gated access."""

from __future__ import annotations

from typing import Any, Callable

try:
    from agentic_assistants.core.patterns import CachingProxy, ProxyBase
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class MockMLModel:
        """Tiny stand-in for a heavyweight model (load + predict)."""

        def __init__(self, name: str = "mock-transformer") -> None:
            self.name = name
            self._loaded = True
            print(f"    (MockMLModel '{name}' constructed - imagine GB weights on disk)")

        def predict(self, x: str) -> str:
            return f"[{self.name}] score={sum(ord(c) for c in x) % 97}"

        def explain(self) -> str:
            return f"architecture={self.name}"

    class _LazyPlaceholder:
        """Stub so ``ProxyBase.__getattr__`` can bind ``predict`` before the real model exists."""

        def predict(self, *_a: Any, **_kw: Any) -> Any:
            raise RuntimeError("LazyModelLoader placeholder - should not run")

    class LazyModelLoader(ProxyBase[Any]):
        """Defers construction of the real model until the first ``predict`` call."""

        def __init__(self, factory: Callable[[], Any]) -> None:
            self._factory = factory
            self._real: Any | None = None
            super().__init__(_LazyPlaceholder())

        def intercept(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
            if self._real is None:
                self._real = self._factory()
                self._subject = self._real
            fn = getattr(self._subject, method_name)
            return fn(*args, **kwargs)

    class PredictionCacheProxy(CachingProxy[Any]):
        """Caches ``predict`` (and other) calls via hash keys (thin alias of CachingProxy)."""

        pass

    class AccessControlProxy(ProxyBase[Any]):
        """Allows only methods present in ``allowed`` for the current principal."""

        def __init__(self, subject: Any, principal: str, allowed: set[str]) -> None:
            super().__init__(subject)
            self._principal = principal
            self._allowed = allowed

        def intercept(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
            if method_name not in self._allowed:
                raise PermissionError(
                    f"principal {self._principal!r} cannot call {method_name!r}"
                )
            fn = getattr(self._subject, method_name)
            return fn(*args, **kwargs)

    def main() -> None:
        print("Proxy pattern: LazyModelLoader, PredictionCacheProxy, AccessControlProxy")
        print("-" * 60)

        print("\n1) LazyModelLoader - no model until first predict:")
        lazy = LazyModelLoader(lambda: MockMLModel("demo-v1"))
        print("  (no load yet)")
        print("  first predict:", lazy.predict("hello"))
        print("  second predict:", lazy.predict("world"))

        print("\n2) PredictionCacheProxy - repeated inputs hit cache:")
        base = MockMLModel("cached")
        cached = PredictionCacheProxy(base, maxsize=64)
        print("  call 1:", cached.predict("same"))
        print("  call 2:", cached.predict("same"))

        print("\n3) AccessControlProxy - role may call predict but not explain:")
        model = MockMLModel("secured")
        user_proxy = AccessControlProxy(model, principal="batch_job", allowed={"predict"})
        print("  predict OK:", user_proxy.predict("ok"))
        try:
            user_proxy.explain()
        except PermissionError as e:
            print("  blocked:", e)

        admin_proxy = AccessControlProxy(model, principal="admin", allowed={"predict", "explain"})
        print("  admin explain:", admin_proxy.explain())


else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
