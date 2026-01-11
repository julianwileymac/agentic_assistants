# Chunk: 025ded03bcca_3

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/mock.pyi`
- lines: 233-326
- chunk: 4/6

```
info: Any) -> None: ...
    def start(self) -> _T: ...
    def stop(self) -> None: ...

class _patch_dict:
    in_dict: Any
    values: Any
    clear: Any
    def __init__(self, in_dict: Any, values: Any = ..., clear: Any = ..., **kwargs: Any) -> None: ...
    def __call__(self, f: Any) -> Any: ...
    def decorate_class(self, klass: Any) -> Any: ...
    def __enter__(self) -> Any: ...
    def __exit__(self, *args: Any) -> Any: ...
    start: Any
    stop: Any

class _patcher:
    TEST_PREFIX: str
    dict: Type[_patch_dict]
    if sys.version_info >= (3, 8):
        @overload
        def __call__(  # type: ignore
            self,
            target: Any,
            *,
            spec: Optional[Any] = ...,
            create: bool = ...,
            spec_set: Optional[Any] = ...,
            autospec: Optional[Any] = ...,
            new_callable: Optional[Any] = ...,
            **kwargs: Any,
        ) -> _patch[Union[MagicMock, AsyncMock]]: ...
        # This overload also covers the case, where new==DEFAULT. In this case, the return type is _patch[Any].
        # Ideally we'd be able to add an overload for it so that the return type is _patch[MagicMock],
        # but that's impossible with the current type system.
        @overload
        def __call__(
            self,
            target: Any,
            new: _T,
            spec: Optional[Any] = ...,
            create: bool = ...,
            spec_set: Optional[Any] = ...,
            autospec: Optional[Any] = ...,
            new_callable: Optional[Any] = ...,
            **kwargs: Any,
        ) -> _patch[_T]: ...
    else:
        @overload
        def __call__(  # type: ignore
            self,
            target: Any,
            *,
            spec: Optional[Any] = ...,
            create: bool = ...,
            spec_set: Optional[Any] = ...,
            autospec: Optional[Any] = ...,
            new_callable: Optional[Any] = ...,
            **kwargs: Any,
        ) -> _patch[MagicMock]: ...
        @overload
        def __call__(
            self,
            target: Any,
            new: _T,
            spec: Optional[Any] = ...,
            create: bool = ...,
            spec_set: Optional[Any] = ...,
            autospec: Optional[Any] = ...,
            new_callable: Optional[Any] = ...,
            **kwargs: Any,
        ) -> _patch[_T]: ...
    if sys.version_info >= (3, 8):
        @overload
        def object(  # type: ignore
            self,
            target: Any,
            attribute: Text,
            *,
            spec: Optional[Any] = ...,
            create: bool = ...,
            spec_set: Optional[Any] = ...,
            autospec: Optional[Any] = ...,
            new_callable: Optional[Any] = ...,
            **kwargs: Any,
        ) -> _patch[Union[MagicMock, AsyncMock]]: ...
        @overload
        def object(
            self,
            target: Any,
            attribute: Text,
            new: _T = ...,
            spec: Optional[Any] = ...,
```
