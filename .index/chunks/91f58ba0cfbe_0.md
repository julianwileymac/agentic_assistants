# Chunk: 91f58ba0cfbe_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/doctest.pyi`
- lines: 1-106
- chunk: 1/3

```
import sys
import types
import unittest
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Type, Union

class TestResults(NamedTuple):
    failed: int
    attempted: int

OPTIONFLAGS_BY_NAME: Dict[str, int]

def register_optionflag(name: str) -> int: ...

DONT_ACCEPT_TRUE_FOR_1: int
DONT_ACCEPT_BLANKLINE: int
NORMALIZE_WHITESPACE: int
ELLIPSIS: int
SKIP: int
IGNORE_EXCEPTION_DETAIL: int

COMPARISON_FLAGS: int

REPORT_UDIFF: int
REPORT_CDIFF: int
REPORT_NDIFF: int
REPORT_ONLY_FIRST_FAILURE: int
if sys.version_info >= (3, 4):
    FAIL_FAST: int

REPORTING_FLAGS: int

BLANKLINE_MARKER: str
ELLIPSIS_MARKER: str

class Example:
    source: str
    want: str
    exc_msg: Optional[str]
    lineno: int
    indent: int
    options: Dict[int, bool]
    def __init__(
        self,
        source: str,
        want: str,
        exc_msg: Optional[str] = ...,
        lineno: int = ...,
        indent: int = ...,
        options: Optional[Dict[int, bool]] = ...,
    ) -> None: ...
    def __hash__(self) -> int: ...

class DocTest:
    examples: List[Example]
    globs: Dict[str, Any]
    name: str
    filename: Optional[str]
    lineno: Optional[int]
    docstring: Optional[str]
    def __init__(
        self,
        examples: List[Example],
        globs: Dict[str, Any],
        name: str,
        filename: Optional[str],
        lineno: Optional[int],
        docstring: Optional[str],
    ) -> None: ...
    def __hash__(self) -> int: ...
    def __lt__(self, other: DocTest) -> bool: ...

class DocTestParser:
    def parse(self, string: str, name: str = ...) -> List[Union[str, Example]]: ...
    def get_doctest(
        self, string: str, globs: Dict[str, Any], name: str, filename: Optional[str], lineno: Optional[int]
    ) -> DocTest: ...
    def get_examples(self, string: str, name: str = ...) -> List[Example]: ...

class DocTestFinder:
    def __init__(
        self, verbose: bool = ..., parser: DocTestParser = ..., recurse: bool = ..., exclude_empty: bool = ...
    ) -> None: ...
    def find(
        self,
        obj: object,
        name: Optional[str] = ...,
        module: Union[None, bool, types.ModuleType] = ...,
        globs: Optional[Dict[str, Any]] = ...,
        extraglobs: Optional[Dict[str, Any]] = ...,
    ) -> List[DocTest]: ...

_Out = Callable[[str], Any]
_ExcInfo = Tuple[Type[BaseException], BaseException, types.TracebackType]

class DocTestRunner:
    DIVIDER: str
    optionflags: int
    original_optionflags: int
    tries: int
    failures: int
    test: DocTest
    def __init__(self, checker: Optional[OutputChecker] = ..., verbose: Optional[bool] = ..., optionflags: int = ...) -> None: ...
    def report_start(self, out: _Out, test: DocTest, example: Example) -> None: ...
    def report_success(self, out: _Out, test: DocTest, example: Example, got: str) -> None: ...
    def report_failure(self, out: _Out, test: DocTest, example: Example, got: str) -> None: ...
```
