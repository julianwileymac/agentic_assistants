# Chunk: 91f58ba0cfbe_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/doctest.pyi`
- lines: 102-186
- chunk: 2/3

```
int = ...) -> None: ...
    def report_start(self, out: _Out, test: DocTest, example: Example) -> None: ...
    def report_success(self, out: _Out, test: DocTest, example: Example, got: str) -> None: ...
    def report_failure(self, out: _Out, test: DocTest, example: Example, got: str) -> None: ...
    def report_unexpected_exception(self, out: _Out, test: DocTest, example: Example, exc_info: _ExcInfo) -> None: ...
    def run(
        self, test: DocTest, compileflags: Optional[int] = ..., out: Optional[_Out] = ..., clear_globs: bool = ...
    ) -> TestResults: ...
    def summarize(self, verbose: Optional[bool] = ...) -> TestResults: ...
    def merge(self, other: DocTestRunner) -> None: ...

class OutputChecker:
    def check_output(self, want: str, got: str, optionflags: int) -> bool: ...
    def output_difference(self, example: Example, got: str, optionflags: int) -> str: ...

class DocTestFailure(Exception):
    test: DocTest
    example: Example
    got: str
    def __init__(self, test: DocTest, example: Example, got: str) -> None: ...

class UnexpectedException(Exception):
    test: DocTest
    example: Example
    exc_info: _ExcInfo
    def __init__(self, test: DocTest, example: Example, exc_info: _ExcInfo) -> None: ...

class DebugRunner(DocTestRunner): ...

master: Optional[DocTestRunner]

def testmod(
    m: Optional[types.ModuleType] = ...,
    name: Optional[str] = ...,
    globs: Optional[Dict[str, Any]] = ...,
    verbose: Optional[bool] = ...,
    report: bool = ...,
    optionflags: int = ...,
    extraglobs: Optional[Dict[str, Any]] = ...,
    raise_on_error: bool = ...,
    exclude_empty: bool = ...,
) -> TestResults: ...
def testfile(
    filename: str,
    module_relative: bool = ...,
    name: Optional[str] = ...,
    package: Union[None, str, types.ModuleType] = ...,
    globs: Optional[Dict[str, Any]] = ...,
    verbose: Optional[bool] = ...,
    report: bool = ...,
    optionflags: int = ...,
    extraglobs: Optional[Dict[str, Any]] = ...,
    raise_on_error: bool = ...,
    parser: DocTestParser = ...,
    encoding: Optional[str] = ...,
) -> TestResults: ...
def run_docstring_examples(
    f: object,
    globs: Dict[str, Any],
    verbose: bool = ...,
    name: str = ...,
    compileflags: Optional[int] = ...,
    optionflags: int = ...,
) -> None: ...
def set_unittest_reportflags(flags: int) -> int: ...

class DocTestCase(unittest.TestCase):
    def __init__(
        self,
        test: DocTest,
        optionflags: int = ...,
        setUp: Optional[Callable[[DocTest], Any]] = ...,
        tearDown: Optional[Callable[[DocTest], Any]] = ...,
        checker: Optional[OutputChecker] = ...,
    ) -> None: ...
    def setUp(self) -> None: ...
    def tearDown(self) -> None: ...
    def runTest(self) -> None: ...
    def format_failure(self, err: str) -> str: ...
    def debug(self) -> None: ...
    def id(self) -> str: ...
    def __hash__(self) -> int: ...
    def shortDescription(self) -> str: ...
```
