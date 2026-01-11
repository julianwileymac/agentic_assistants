# Chunk: 6bbc9fe7cf6b_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/unittest.pyi`
- lines: 1-98
- chunk: 1/5

```
import datetime
import types
from abc import ABCMeta, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Mapping,
    NoReturn,
    Optional,
    Pattern,
    Sequence,
    Set,
    Text,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

_T = TypeVar("_T")
_FT = TypeVar("_FT")

_ExceptionType = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
_Regexp = Union[Text, Pattern[Text]]

_SysExcInfoType = Union[Tuple[Type[BaseException], BaseException, types.TracebackType], Tuple[None, None, None]]

class Testable(metaclass=ABCMeta):
    @abstractmethod
    def run(self, result: TestResult) -> None: ...
    @abstractmethod
    def debug(self) -> None: ...
    @abstractmethod
    def countTestCases(self) -> int: ...

# TODO ABC for test runners?

class TestResult:
    errors: List[Tuple[TestCase, str]]
    failures: List[Tuple[TestCase, str]]
    skipped: List[Tuple[TestCase, str]]
    expectedFailures: List[Tuple[TestCase, str]]
    unexpectedSuccesses: List[TestCase]
    shouldStop: bool
    testsRun: int
    buffer: bool
    failfast: bool
    def wasSuccessful(self) -> bool: ...
    def stop(self) -> None: ...
    def startTest(self, test: TestCase) -> None: ...
    def stopTest(self, test: TestCase) -> None: ...
    def startTestRun(self) -> None: ...
    def stopTestRun(self) -> None: ...
    def addError(self, test: TestCase, err: _SysExcInfoType) -> None: ...
    def addFailure(self, test: TestCase, err: _SysExcInfoType) -> None: ...
    def addSuccess(self, test: TestCase) -> None: ...
    def addSkip(self, test: TestCase, reason: str) -> None: ...
    def addExpectedFailure(self, test: TestCase, err: str) -> None: ...
    def addUnexpectedSuccess(self, test: TestCase) -> None: ...

class _AssertRaisesBaseContext:
    expected: Any
    failureException: Type[BaseException]
    obj_name: str
    expected_regex: Pattern[str]

class _AssertRaisesContext(_AssertRaisesBaseContext):
    exception: Any
    def __enter__(self) -> _AssertRaisesContext: ...
    def __exit__(self, exc_type, exc_value, tb) -> bool: ...

class TestCase(Testable):
    failureException: Type[BaseException]
    longMessage: bool
    maxDiff: Optional[int]
    # undocumented
    _testMethodName: str
    def __init__(self, methodName: str = ...) -> None: ...
    def setUp(self) -> None: ...
    def tearDown(self) -> None: ...
    @classmethod
    def setUpClass(cls) -> None: ...
    @classmethod
    def tearDownClass(cls) -> None: ...
    def run(self, result: TestResult = ...) -> None: ...
    def debug(self) -> None: ...
    def assert_(self, expr: Any, msg: object = ...) -> None: ...
    def failUnless(self, expr: Any, msg: object = ...) -> None: ...
    def assertTrue(self, expr: Any, msg: object = ...) -> None: ...
    def assertEqual(self, first: Any, second: Any, msg: object = ...) -> None: ...
```
