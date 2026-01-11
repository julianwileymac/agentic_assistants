# Chunk: 2ac4d72dae1c_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/types.pyi`
- lines: 103-182
- chunk: 2/4

```
        nlocals: int,
            stacksize: int,
            flags: int,
            codestring: bytes,
            constants: Tuple[Any, ...],
            names: Tuple[str, ...],
            varnames: Tuple[str, ...],
            filename: str,
            name: str,
            firstlineno: int,
            lnotab: bytes,
            freevars: Tuple[str, ...] = ...,
            cellvars: Tuple[str, ...] = ...,
        ) -> None: ...
    if sys.version_info >= (3, 8):
        def replace(
            self,
            *,
            co_argcount: int = ...,
            co_posonlyargcount: int = ...,
            co_kwonlyargcount: int = ...,
            co_nlocals: int = ...,
            co_stacksize: int = ...,
            co_flags: int = ...,
            co_firstlineno: int = ...,
            co_code: bytes = ...,
            co_consts: Tuple[Any, ...] = ...,
            co_names: Tuple[str, ...] = ...,
            co_varnames: Tuple[str, ...] = ...,
            co_freevars: Tuple[str, ...] = ...,
            co_cellvars: Tuple[str, ...] = ...,
            co_filename: str = ...,
            co_name: str = ...,
            co_lnotab: bytes = ...,
        ) -> CodeType: ...

class MappingProxyType(Mapping[_KT, _VT], Generic[_KT, _VT]):
    def __init__(self, mapping: Mapping[_KT, _VT]) -> None: ...
    def __getitem__(self, k: _KT) -> _VT: ...
    def __iter__(self) -> Iterator[_KT]: ...
    def __len__(self) -> int: ...
    def copy(self) -> Dict[_KT, _VT]: ...

class SimpleNamespace:
    def __init__(self, **kwargs: Any) -> None: ...
    def __getattribute__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __delattr__(self, name: str) -> None: ...

class GeneratorType:
    gi_code: CodeType
    gi_frame: FrameType
    gi_running: bool
    gi_yieldfrom: Optional[GeneratorType]
    def __iter__(self) -> GeneratorType: ...
    def __next__(self) -> Any: ...
    def close(self) -> None: ...
    def send(self, __arg: Any) -> Any: ...
    @overload
    def throw(
        self, __typ: Type[BaseException], __val: Union[BaseException, object] = ..., __tb: Optional[TracebackType] = ...
    ) -> Any: ...
    @overload
    def throw(self, __typ: BaseException, __val: None = ..., __tb: Optional[TracebackType] = ...) -> Any: ...

class AsyncGeneratorType(Generic[_T_co, _T_contra]):
    ag_await: Optional[Awaitable[Any]]
    ag_frame: FrameType
    ag_running: bool
    ag_code: CodeType
    def __aiter__(self) -> Awaitable[AsyncGeneratorType[_T_co, _T_contra]]: ...
    def __anext__(self) -> Awaitable[_T_co]: ...
    def asend(self, __val: _T_contra) -> Awaitable[_T_co]: ...
    @overload
    def athrow(
        self, __typ: Type[BaseException], __val: Union[BaseException, object] = ..., __tb: Optional[TracebackType] = ...
    ) -> Awaitable[_T_co]: ...
    @overload
    def athrow(self, __typ: BaseException, __val: None = ..., __tb: Optional[TracebackType] = ...) -> Awaitable[_T_co]: ...
```
