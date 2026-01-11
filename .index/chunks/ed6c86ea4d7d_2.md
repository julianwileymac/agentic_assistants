# Chunk: ed6c86ea4d7d_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/sys.pyi`
- lines: 210-236
- chunk: 3/3

```
t: ...  # Debug builds only

if sys.version_info < (3, 9):
    def getcheckinterval() -> int: ...  # deprecated
    def setcheckinterval(__n: int) -> None: ...  # deprecated

if sys.version_info >= (3, 8):
    # not exported by sys
    class UnraisableHookArgs:
        exc_type: Type[BaseException]
        exc_value: Optional[BaseException]
        exc_traceback: Optional[TracebackType]
        err_msg: Optional[str]
        object: Optional[_object]
    unraisablehook: Callable[[UnraisableHookArgs], Any]
    def addaudithook(hook: Callable[[str, Tuple[Any, ...]], Any]) -> None: ...
    def audit(__event: str, *args: Any) -> None: ...

_AsyncgenHook = Optional[Callable[[AsyncGenerator[Any, Any]], None]]

class _asyncgen_hooks(Tuple[_AsyncgenHook, _AsyncgenHook]):
    firstiter: _AsyncgenHook
    finalizer: _AsyncgenHook

def get_asyncgen_hooks() -> _asyncgen_hooks: ...
def set_asyncgen_hooks(firstiter: _AsyncgenHook = ..., finalizer: _AsyncgenHook = ...) -> None: ...
```
