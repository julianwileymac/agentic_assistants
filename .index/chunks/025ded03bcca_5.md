# Chunk: 025ded03bcca_5

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/mock.pyi`
- lines: 393-442
- chunk: 6/6

```
(self, *args, **kwargs) -> None: ...
        await_count: int
        await_args: Optional[_Call]
        await_args_list: _CallList
    class AsyncMagicMixin(MagicMixin):
        def __init__(self, *args: Any, **kw: Any) -> None: ...
    class AsyncMock(AsyncMockMixin, AsyncMagicMixin, Mock): ...

class MagicProxy:
    name: Any
    parent: Any
    def __init__(self, name: Any, parent: Any) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def create_mock(self) -> Any: ...
    def __get__(self, obj: Any, _type: Optional[Any] = ...) -> Any: ...

class _ANY:
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...

ANY: Any

def create_autospec(
    spec: Any, spec_set: Any = ..., instance: Any = ..., _parent: Optional[Any] = ..., _name: Optional[Any] = ..., **kwargs: Any
) -> Any: ...

class _SpecState:
    spec: Any
    ids: Any
    spec_set: Any
    parent: Any
    instance: Any
    name: Any
    def __init__(
        self,
        spec: Any,
        spec_set: Any = ...,
        parent: Optional[Any] = ...,
        name: Optional[Any] = ...,
        ids: Optional[Any] = ...,
        instance: Any = ...,
    ) -> None: ...

def mock_open(mock: Optional[Any] = ..., read_data: Any = ...) -> Any: ...

PropertyMock = Any

if sys.version_info >= (3, 7):
    def seal(mock: Any) -> None: ...
```
