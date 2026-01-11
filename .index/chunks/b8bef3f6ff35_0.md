# Chunk: b8bef3f6ff35_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/unittest/signals.pyi`
- lines: 1-13
- chunk: 1/1

```
import unittest.result
from typing import Any, Callable, TypeVar, overload

_F = TypeVar("_F", bound=Callable[..., Any])

def installHandler() -> None: ...
def registerResult(result: unittest.result.TestResult) -> None: ...
def removeResult(result: unittest.result.TestResult) -> bool: ...
@overload
def removeHandler(method: None = ...) -> None: ...
@overload
def removeHandler(method: _F) -> _F: ...
```
