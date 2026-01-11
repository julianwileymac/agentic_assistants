# Chunk: 8975deaade3c_3

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/more_itertools/more.pyi`
- lines: 282-377
- chunk: 4/8

```
rator[tuple[_T | _U, ...]]: ...
def sort_together(
    iterables: Iterable[Iterable[_T]],
    key_list: Iterable[int] = ...,
    key: Callable[..., Any] | None = ...,
    reverse: bool = ...,
) -> list[tuple[_T, ...]]: ...
def unzip(iterable: Iterable[Sequence[_T]]) -> tuple[Iterator[_T], ...]: ...
def divide(n: int, iterable: Iterable[_T]) -> list[Iterator[_T]]: ...
def always_iterable(
    obj: object,
    base_type: type | tuple[type | tuple[Any, ...], ...] | None = ...,
) -> Iterator[Any]: ...
def adjacent(
    predicate: Callable[[_T], bool],
    iterable: Iterable[_T],
    distance: int = ...,
) -> Iterator[tuple[bool, _T]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: None = None,
    valuefunc: None = None,
    reducefunc: None = None,
) -> Iterator[tuple[_T, Iterator[_T]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: None,
    reducefunc: None,
) -> Iterator[tuple[_U, Iterator[_T]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: None,
    valuefunc: Callable[[_T], _V],
    reducefunc: None,
) -> Iterable[tuple[_T, Iterable[_V]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: Callable[[_T], _V],
    reducefunc: None,
) -> Iterable[tuple[_U, Iterator[_V]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: None,
    valuefunc: None,
    reducefunc: Callable[[Iterator[_T]], _W],
) -> Iterable[tuple[_T, _W]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: None,
    reducefunc: Callable[[Iterator[_T]], _W],
) -> Iterable[tuple[_U, _W]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: None,
    valuefunc: Callable[[_T], _V],
    reducefunc: Callable[[Iterable[_V]], _W],
) -> Iterable[tuple[_T, _W]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: Callable[[_T], _V],
    reducefunc: Callable[[Iterable[_V]], _W],
) -> Iterable[tuple[_U, _W]]: ...

class numeric_range(Generic[_T, _U], Sequence[_T], Hashable, Reversible[_T]):
    @overload
    def __init__(self, __stop: _T) -> None: ...
    @overload
    def __init__(self, __start: _T, __stop: _T) -> None: ...
    @overload
    def __init__(self, __start: _T, __stop: _T, __step: _U) -> None: ...
    def __bool__(self) -> bool: ...
    def __contains__(self, elem: object) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    @overload
    def __getitem__(self, key: int) -> _T: ...
    @overload
    def __getitem__(self, key: slice) -> numeric_range[_T, _U]: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[_T]: ...
    def __len__(self) -> int: ...
    def __reduce__(
        self,
    ) -> tuple[Type[numeric_range[_T, _U]], tuple[_T, _T, _U]]: ...
```
