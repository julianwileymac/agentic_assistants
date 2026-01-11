# Chunk: 6bbc9fe7cf6b_4

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/unittest.pyi`
- lines: 222-281
- chunk: 5/5

```
stCaseNames(self, testCaseClass: Type[TestCase] = ...) -> List[str]: ...

defaultTestLoader: TestLoader

class TextTestResult(TestResult):
    def __init__(self, stream: TextIO, descriptions: bool, verbosity: int) -> None: ...
    def getDescription(self, test: TestCase) -> str: ...  # undocumented
    def printErrors(self) -> None: ...  # undocumented
    def printErrorList(self, flavour: str, errors: List[Tuple[TestCase, str]]) -> None: ...  # undocumented

class TextTestRunner:
    def __init__(
        self,
        stream: Optional[TextIO] = ...,
        descriptions: bool = ...,
        verbosity: int = ...,
        failfast: bool = ...,
        buffer: bool = ...,
        resultclass: Optional[Type[TestResult]] = ...,
    ) -> None: ...
    def _makeResult(self) -> TestResult: ...
    def run(self, test: Testable) -> TestResult: ...  # undocumented

class SkipTest(Exception): ...

# TODO precise types
def skipUnless(condition: Any, reason: Union[str, unicode]) -> Any: ...
def skipIf(condition: Any, reason: Union[str, unicode]) -> Any: ...
def expectedFailure(func: _FT) -> _FT: ...
def skip(reason: Union[str, unicode]) -> Any: ...

# not really documented
class TestProgram:
    result: TestResult
    def runTests(self) -> None: ...  # undocumented

def main(
    module: Union[None, Text, types.ModuleType] = ...,
    defaultTest: Optional[str] = ...,
    argv: Optional[Sequence[str]] = ...,
    testRunner: Union[Type[TextTestRunner], TextTestRunner, None] = ...,
    testLoader: TestLoader = ...,
    exit: bool = ...,
    verbosity: int = ...,
    failfast: Optional[bool] = ...,
    catchbreak: Optional[bool] = ...,
    buffer: Optional[bool] = ...,
) -> TestProgram: ...
def load_tests(loader: TestLoader, tests: TestSuite, pattern: Optional[Text]) -> TestSuite: ...
def installHandler() -> None: ...
def registerResult(result: TestResult) -> None: ...
def removeResult(result: TestResult) -> bool: ...
@overload
def removeHandler() -> None: ...
@overload
def removeHandler(function: Callable[..., Any]) -> Callable[..., Any]: ...

# private but occasionally used
util: types.ModuleType
```
