# Chunk: 8975deaade3c_7

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/more_itertools/more.pyi`
- lines: 619-710
- chunk: 8/8

```
es_everseen(
    iterable: Iterable[_T], key: Callable[[_T], _U] | None = ...
) -> Iterator[_T]: ...
def duplicates_justseen(
    iterable: Iterable[_T], key: Callable[[_T], _U] | None = ...
) -> Iterator[_T]: ...
def classify_unique(
    iterable: Iterable[_T], key: Callable[[_T], _U] | None = ...
) -> Iterator[tuple[_T, bool, bool]]: ...

class _SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool: ...

_SupportsLessThanT = TypeVar("_SupportsLessThanT", bound=_SupportsLessThan)

@overload
def minmax(
    iterable_or_value: Iterable[_SupportsLessThanT], *, key: None = None
) -> tuple[_SupportsLessThanT, _SupportsLessThanT]: ...
@overload
def minmax(
    iterable_or_value: Iterable[_T], *, key: Callable[[_T], _SupportsLessThan]
) -> tuple[_T, _T]: ...
@overload
def minmax(
    iterable_or_value: Iterable[_SupportsLessThanT],
    *,
    key: None = None,
    default: _U,
) -> _U | tuple[_SupportsLessThanT, _SupportsLessThanT]: ...
@overload
def minmax(
    iterable_or_value: Iterable[_T],
    *,
    key: Callable[[_T], _SupportsLessThan],
    default: _U,
) -> _U | tuple[_T, _T]: ...
@overload
def minmax(
    iterable_or_value: _SupportsLessThanT,
    __other: _SupportsLessThanT,
    *others: _SupportsLessThanT,
) -> tuple[_SupportsLessThanT, _SupportsLessThanT]: ...
@overload
def minmax(
    iterable_or_value: _T,
    __other: _T,
    *others: _T,
    key: Callable[[_T], _SupportsLessThan],
) -> tuple[_T, _T]: ...
def longest_common_prefix(
    iterables: Iterable[Iterable[_T]],
) -> Iterator[_T]: ...
def iequals(*iterables: Iterable[Any]) -> bool: ...
def constrained_batches(
    iterable: Iterable[_T],
    max_size: int,
    max_count: int | None = ...,
    get_len: Callable[[_T], object] = ...,
    strict: bool = ...,
) -> Iterator[tuple[_T]]: ...
def gray_product(*iterables: Iterable[_T]) -> Iterator[tuple[_T, ...]]: ...
def partial_product(*iterables: Iterable[_T]) -> Iterator[tuple[_T, ...]]: ...
def takewhile_inclusive(
    predicate: Callable[[_T], bool], iterable: Iterable[_T]
) -> Iterator[_T]: ...
def outer_product(
    func: Callable[[_T, _U], _V],
    xs: Iterable[_T],
    ys: Iterable[_U],
    *args: Any,
    **kwargs: Any,
) -> Iterator[tuple[_V, ...]]: ...
def iter_suppress(
    iterable: Iterable[_T],
    *exceptions: Type[BaseException],
) -> Iterator[_T]: ...
def filter_map(
    func: Callable[[_T], _V | None],
    iterable: Iterable[_T],
) -> Iterator[_V]: ...
def powerset_of_sets(iterable: Iterable[_T]) -> Iterator[set[_T]]: ...
def join_mappings(
    **field_to_map: Mapping[_T, _V]
) -> dict[_T, dict[str, _V]]: ...
def doublestarmap(
    func: Callable[..., _T],
    iterable: Iterable[Mapping[str, Any]],
) -> Iterator[_T]: ...
def dft(xarr: Sequence[complex]) -> Iterator[complex]: ...
def idft(Xarr: Sequence[complex]) -> Iterator[complex]: ...
```
