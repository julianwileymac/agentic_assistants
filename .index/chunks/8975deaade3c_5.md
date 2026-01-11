# Chunk: 8975deaade3c_5

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/more_itertools/more.pyi`
- lines: 448-548
- chunk: 6/8

```
 run_length:
    @staticmethod
    def encode(iterable: Iterable[_T]) -> Iterator[tuple[_T, int]]: ...
    @staticmethod
    def decode(iterable: Iterable[tuple[_T, int]]) -> Iterator[_T]: ...

def exactly_n(
    iterable: Iterable[_T], n: int, predicate: Callable[[_T], object] = ...
) -> bool: ...
def circular_shifts(iterable: Iterable[_T]) -> list[tuple[_T, ...]]: ...
def make_decorator(
    wrapping_func: Callable[..., _U], result_index: int = ...
) -> Callable[..., Callable[[Callable[..., Any]], Callable[..., _U]]]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: None = ...,
    reducefunc: None = ...,
) -> dict[_U, list[_T]]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: Callable[[_T], _V],
    reducefunc: None = ...,
) -> dict[_U, list[_V]]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: None = ...,
    reducefunc: Callable[[list[_T]], _W] = ...,
) -> dict[_U, _W]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _U],
    valuefunc: Callable[[_T], _V],
    reducefunc: Callable[[list[_V]], _W],
) -> dict[_U, _W]: ...
def rlocate(
    iterable: Iterable[_T],
    pred: Callable[..., object] = ...,
    window_size: int | None = ...,
) -> Iterator[int]: ...
def replace(
    iterable: Iterable[_T],
    pred: Callable[..., object],
    substitutes: Iterable[_U],
    count: int | None = ...,
    window_size: int = ...,
) -> Iterator[_T | _U]: ...
def partitions(iterable: Iterable[_T]) -> Iterator[list[list[_T]]]: ...
def set_partitions(
    iterable: Iterable[_T], k: int | None = ...
) -> Iterator[list[list[_T]]]: ...

class time_limited(Generic[_T], Iterator[_T]):
    def __init__(
        self, limit_seconds: float, iterable: Iterable[_T]
    ) -> None: ...
    def __iter__(self) -> islice_extended[_T]: ...
    def __next__(self) -> _T: ...

@overload
def only(
    iterable: Iterable[_T], *, too_long: _Raisable | None = ...
) -> _T | None: ...
@overload
def only(
    iterable: Iterable[_T], default: _U, too_long: _Raisable | None = ...
) -> _T | _U: ...
def ichunked(iterable: Iterable[_T], n: int) -> Iterator[Iterator[_T]]: ...
def distinct_combinations(
    iterable: Iterable[_T], r: int
) -> Iterator[tuple[_T, ...]]: ...
def filter_except(
    validator: Callable[[Any], object],
    iterable: Iterable[_T],
    *exceptions: Type[BaseException],
) -> Iterator[_T]: ...
def map_except(
    function: Callable[[Any], _U],
    iterable: Iterable[_T],
    *exceptions: Type[BaseException],
) -> Iterator[_U]: ...
def map_if(
    iterable: Iterable[Any],
    pred: Callable[[Any], bool],
    func: Callable[[Any], Any],
    func_else: Callable[[Any], Any] | None = ...,
) -> Iterator[Any]: ...
def sample(
    iterable: Iterable[_T],
    k: int,
    weights: Iterable[float] | None = ...,
) -> list[_T]: ...
def is_sorted(
    iterable: Iterable[_T],
```
