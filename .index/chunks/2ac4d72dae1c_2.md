# Chunk: 2ac4d72dae1c_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/types.pyi`
- lines: 177-256
- chunk: 3/4

```
f athrow(
        self, __typ: Type[BaseException], __val: Union[BaseException, object] = ..., __tb: Optional[TracebackType] = ...
    ) -> Awaitable[_T_co]: ...
    @overload
    def athrow(self, __typ: BaseException, __val: None = ..., __tb: Optional[TracebackType] = ...) -> Awaitable[_T_co]: ...
    def aclose(self) -> Awaitable[None]: ...

class CoroutineType:
    cr_await: Optional[Any]
    cr_code: CodeType
    cr_frame: FrameType
    cr_running: bool
    def close(self) -> None: ...
    def send(self, __arg: Any) -> Any: ...
    @overload
    def throw(
        self, __typ: Type[BaseException], __val: Union[BaseException, object] = ..., __tb: Optional[TracebackType] = ...
    ) -> Any: ...
    @overload
    def throw(self, __typ: BaseException, __val: None = ..., __tb: Optional[TracebackType] = ...) -> Any: ...

class _StaticFunctionType:
    """Fictional type to correct the type of MethodType.__func__.

    FunctionType is a descriptor, so mypy follows the descriptor protocol and
    converts MethodType.__func__ back to MethodType (the return type of
    FunctionType.__get__). But this is actually a special case; MethodType is
    implemented in C and its attribute access doesn't go through
    __getattribute__.

    By wrapping FunctionType in _StaticFunctionType, we get the right result;
    similar to wrapping a function in staticmethod() at runtime to prevent it
    being bound as a method.
    """

    def __get__(self, obj: Optional[object], type: Optional[type]) -> FunctionType: ...

class MethodType:
    __func__: _StaticFunctionType
    __self__: object
    __name__: str
    __qualname__: str
    def __init__(self, func: Callable[..., Any], obj: object) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

class BuiltinFunctionType:
    __self__: Union[object, ModuleType]
    __name__: str
    __qualname__: str
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

BuiltinMethodType = BuiltinFunctionType

if sys.version_info >= (3, 7):
    class WrapperDescriptorType:
        __name__: str
        __qualname__: str
        __objclass__: type
        def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
        def __get__(self, obj: Any, type: type = ...) -> Any: ...
    class MethodWrapperType:
        __self__: object
        __name__: str
        __qualname__: str
        __objclass__: type
        def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
        def __eq__(self, other: Any) -> bool: ...
        def __ne__(self, other: Any) -> bool: ...
    class MethodDescriptorType:
        __name__: str
        __qualname__: str
        __objclass__: type
        def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
        def __get__(self, obj: Any, type: type = ...) -> Any: ...
    class ClassMethodDescriptorType:
        __name__: str
        __qualname__: str
        __objclass__: type
        def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
```
