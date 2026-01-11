# Chunk: 8975deaade3c_2

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/more_itertools/more.pyi`
- lines: 180-290
- chunk: 3/8

```
oad
def padded(
    iterable: Iterable[_T],
    *,
    n: int | None = ...,
    next_multiple: bool = ...,
) -> Iterator[_T | None]: ...
@overload
def padded(
    iterable: Iterable[_T],
    fillvalue: _U,
    n: int | None = ...,
    next_multiple: bool = ...,
) -> Iterator[_T | _U]: ...
@overload
def repeat_last(iterable: Iterable[_T]) -> Iterator[_T]: ...
@overload
def repeat_last(iterable: Iterable[_T], default: _U) -> Iterator[_T | _U]: ...
def distribute(n: int, iterable: Iterable[_T]) -> list[Iterator[_T]]: ...
@overload
def stagger(
    iterable: Iterable[_T],
    offsets: _SizedIterable[int] = ...,
    longest: bool = ...,
) -> Iterator[tuple[_T | None, ...]]: ...
@overload
def stagger(
    iterable: Iterable[_T],
    offsets: _SizedIterable[int] = ...,
    longest: bool = ...,
    fillvalue: _U = ...,
) -> Iterator[tuple[_T | _U, ...]]: ...

class UnequalIterablesError(ValueError):
    def __init__(self, details: tuple[int, int, int] | None = ...) -> None: ...

@overload
def zip_equal(__iter1: Iterable[_T1]) -> Iterator[tuple[_T1]]: ...
@overload
def zip_equal(
    __iter1: Iterable[_T1], __iter2: Iterable[_T2]
) -> Iterator[tuple[_T1, _T2]]: ...
@overload
def zip_equal(
    __iter1: Iterable[_T],
    __iter2: Iterable[_T],
    __iter3: Iterable[_T],
    *iterables: Iterable[_T],
) -> Iterator[tuple[_T, ...]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T1],
    *,
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: None = None,
) -> Iterator[tuple[_T1 | None]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T1],
    __iter2: Iterable[_T2],
    *,
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: None = None,
) -> Iterator[tuple[_T1 | None, _T2 | None]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T],
    __iter2: Iterable[_T],
    __iter3: Iterable[_T],
    *iterables: Iterable[_T],
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: None = None,
) -> Iterator[tuple[_T | None, ...]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T1],
    *,
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: _U,
) -> Iterator[tuple[_T1 | _U]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T1],
    __iter2: Iterable[_T2],
    *,
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: _U,
) -> Iterator[tuple[_T1 | _U, _T2 | _U]]: ...
@overload
def zip_offset(
    __iter1: Iterable[_T],
    __iter2: Iterable[_T],
    __iter3: Iterable[_T],
    *iterables: Iterable[_T],
    offsets: _SizedIterable[int],
    longest: bool = ...,
    fillvalue: _U,
) -> Iterator[tuple[_T | _U, ...]]: ...
def sort_together(
    iterables: Iterable[Iterable[_T]],
    key_list: Iterable[int] = ...,
    key: Callable[..., Any] | None = ...,
    reverse: bool = ...,
) -> list[tuple[_T, ...]]: ...
def unzip(iterable: Iterable[Sequence[_T]]) -> tuple[Iterator[_T], ...]: ...
```
