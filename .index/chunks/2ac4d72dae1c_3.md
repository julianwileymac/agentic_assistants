# Chunk: 2ac4d72dae1c_3

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/types.pyi`
- lines: 249-335
- chunk: 4/4

```
f __call__(self, *args: Any, **kwargs: Any) -> Any: ...
        def __get__(self, obj: Any, type: type = ...) -> Any: ...
    class ClassMethodDescriptorType:
        __name__: str
        __qualname__: str
        __objclass__: type
        def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
        def __get__(self, obj: Any, type: type = ...) -> Any: ...

class TracebackType:
    if sys.version_info >= (3, 7):
        def __init__(self, tb_next: Optional[TracebackType], tb_frame: FrameType, tb_lasti: int, tb_lineno: int) -> None: ...
        tb_next: Optional[TracebackType]
    else:
        @property
        def tb_next(self) -> Optional[TracebackType]: ...
    # the rest are read-only even in 3.7
    @property
    def tb_frame(self) -> FrameType: ...
    @property
    def tb_lasti(self) -> int: ...
    @property
    def tb_lineno(self) -> int: ...

class FrameType:
    f_back: Optional[FrameType]
    f_builtins: Dict[str, Any]
    f_code: CodeType
    f_globals: Dict[str, Any]
    f_lasti: int
    f_lineno: int
    f_locals: Dict[str, Any]
    f_trace: Optional[Callable[[FrameType, str, Any], Any]]
    if sys.version_info >= (3, 7):
        f_trace_lines: bool
        f_trace_opcodes: bool
    def clear(self) -> None: ...

class GetSetDescriptorType:
    __name__: str
    __objclass__: type
    def __get__(self, obj: Any, type: type = ...) -> Any: ...
    def __set__(self, obj: Any) -> None: ...
    def __delete__(self, obj: Any) -> None: ...

class MemberDescriptorType:
    __name__: str
    __objclass__: type
    def __get__(self, obj: Any, type: type = ...) -> Any: ...
    def __set__(self, obj: Any) -> None: ...
    def __delete__(self, obj: Any) -> None: ...

if sys.version_info >= (3, 7):
    def new_class(
        name: str, bases: Iterable[object] = ..., kwds: Dict[str, Any] = ..., exec_body: Callable[[Dict[str, Any]], None] = ...
    ) -> type: ...
    def resolve_bases(bases: Iterable[object]) -> Tuple[Any, ...]: ...

else:
    def new_class(
        name: str, bases: Tuple[type, ...] = ..., kwds: Dict[str, Any] = ..., exec_body: Callable[[Dict[str, Any]], None] = ...
    ) -> type: ...

def prepare_class(
    name: str, bases: Tuple[type, ...] = ..., kwds: Dict[str, Any] = ...
) -> Tuple[type, Dict[str, Any], Dict[str, Any]]: ...

# Actually a different type, but `property` is special and we want that too.
DynamicClassAttribute = property

def coroutine(f: Callable[..., Any]) -> CoroutineType: ...

if sys.version_info >= (3, 9):
    class GenericAlias:
        __origin__: type
        __args__: Tuple[Any, ...]
        __parameters__: Tuple[Any, ...]
        def __init__(self, origin: type, args: Any) -> None: ...
        def __getattr__(self, name: str) -> Any: ...  # incomplete

if sys.version_info >= (3, 10):
    @final
    class NoneType:
        def __bool__(self) -> Literal[False]: ...
    EllipsisType = ellipsis  # noqa F811 from builtins
    NotImplementedType = _NotImplementedType  # noqa F811 from builtins
```
