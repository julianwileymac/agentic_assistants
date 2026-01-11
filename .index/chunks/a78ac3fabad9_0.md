# Chunk: a78ac3fabad9_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/cachetools/func.pyi`
- lines: 1-12
- chunk: 1/1

```
from typing import Any, Callable, Optional, Sequence, TypeVar

_T = TypeVar("_T")

_F = TypeVar("_F", bound=Callable[..., Any])
_RET = Callable[[_F], _F]

def lfu_cache(maxsize: int = ..., typed: bool = ...) -> _RET: ...
def lru_cache(maxsize: int = ..., typed: bool = ...) -> _RET: ...
def rr_cache(maxsize: int = ..., choice: Optional[Callable[[Sequence[_T]], _T]] = ..., typed: bool = ...) -> _RET: ...
def ttl_cache(maxsize: int = ..., ttl: float = ..., timer: float = ..., typed: bool = ...) -> _RET: ...
```
