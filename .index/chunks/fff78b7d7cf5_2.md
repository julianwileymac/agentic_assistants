# Chunk: fff78b7d7cf5_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/_dummy_threading.pyi`
- lines: 163-188
- chunk: 3/3

```
ass Timer(Thread):
    if sys.version_info >= (3,):
        def __init__(
            self,
            interval: float,
            function: Callable[..., Any],
            args: Optional[Iterable[Any]] = ...,
            kwargs: Optional[Mapping[str, Any]] = ...,
        ) -> None: ...
    else:
        def __init__(
            self, interval: float, function: Callable[..., Any], args: Iterable[Any] = ..., kwargs: Mapping[str, Any] = ...
        ) -> None: ...
    def cancel(self) -> None: ...

if sys.version_info >= (3,):
    class Barrier:
        parties: int
        n_waiting: int
        broken: bool
        def __init__(self, parties: int, action: Optional[Callable[[], None]] = ..., timeout: Optional[float] = ...) -> None: ...
        def wait(self, timeout: Optional[float] = ...) -> int: ...
        def reset(self) -> None: ...
        def abort(self) -> None: ...
    class BrokenBarrierError(RuntimeError): ...
```
