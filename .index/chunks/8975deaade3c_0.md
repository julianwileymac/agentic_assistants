# Chunk: 8975deaade3c_0

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/more_itertools/more.pyi`
- lines: 1-109
- chunk: 1/8

```
"""Stubs for more_itertools.more"""

from __future__ import annotations

from types import TracebackType
from typing import (
    Any,
    Callable,
    Container,
    ContextManager,
    Generic,
    Hashable,
    Mapping,
    Iterable,
    Iterator,
    Mapping,
    overload,
    Reversible,
    Sequence,
    Sized,
    Type,
    TypeVar,
    type_check_only,
)
from typing_extensions import Protocol

# Type and type variable definitions
_T = TypeVar('_T')
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_U = TypeVar('_U')
_V = TypeVar('_V')
_W = TypeVar('_W')
_T_co = TypeVar('_T_co', covariant=True)
_GenFn = TypeVar('_GenFn', bound=Callable[..., Iterator[Any]])
_Raisable = BaseException | Type[BaseException]

@type_check_only
class _SizedIterable(Protocol[_T_co], Sized, Iterable[_T_co]): ...

@type_check_only
class _SizedReversible(Protocol[_T_co], Sized, Reversible[_T_co]): ...

@type_check_only
class _SupportsSlicing(Protocol[_T_co]):
    def __getitem__(self, __k: slice) -> _T_co: ...

def chunked(
    iterable: Iterable[_T], n: int | None, strict: bool = ...
) -> Iterator[list[_T]]: ...
@overload
def first(iterable: Iterable[_T]) -> _T: ...
@overload
def first(iterable: Iterable[_T], default: _U) -> _T | _U: ...
@overload
def last(iterable: Iterable[_T]) -> _T: ...
@overload
def last(iterable: Iterable[_T], default: _U) -> _T | _U: ...
@overload
def nth_or_last(iterable: Iterable[_T], n: int) -> _T: ...
@overload
def nth_or_last(iterable: Iterable[_T], n: int, default: _U) -> _T | _U: ...

class peekable(Generic[_T], Iterator[_T]):
    def __init__(self, iterable: Iterable[_T]) -> None: ...
    def __iter__(self) -> peekable[_T]: ...
    def __bool__(self) -> bool: ...
    @overload
    def peek(self) -> _T: ...
    @overload
    def peek(self, default: _U) -> _T | _U: ...
    def prepend(self, *items: _T) -> None: ...
    def __next__(self) -> _T: ...
    @overload
    def __getitem__(self, index: int) -> _T: ...
    @overload
    def __getitem__(self, index: slice) -> list[_T]: ...

def consumer(func: _GenFn) -> _GenFn: ...
def ilen(iterable: Iterable[_T]) -> int: ...
def iterate(func: Callable[[_T], _T], start: _T) -> Iterator[_T]: ...
def with_iter(
    context_manager: ContextManager[Iterable[_T]],
) -> Iterator[_T]: ...
def one(
    iterable: Iterable[_T],
    too_short: _Raisable | None = ...,
    too_long: _Raisable | None = ...,
) -> _T: ...
def raise_(exception: _Raisable, *args: Any) -> None: ...
def strictly_n(
    iterable: Iterable[_T],
    n: int,
    too_short: _GenFn | None = ...,
    too_long: _GenFn | None = ...,
) -> list[_T]: ...
def distinct_permutations(
    iterable: Iterable[_T], r: int | None = ...
) -> Iterator[tuple[_T, ...]]: ...
def intersperse(
    e: _U, iterable: Iterable[_T], n: int = ...
) -> Iterator[_T | _U]: ...
def unique_to_each(*iterables: Iterable[_T]) -> list[list[_T]]: ...
@overload
def windowed(
    seq: Iterable[_T], n: int, *, step: int = ...
) -> Iterator[tuple[_T | None, ...]]: ...
@overload
```
