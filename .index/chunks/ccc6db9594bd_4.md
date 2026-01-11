# Chunk: ccc6db9594bd_4

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 344-438
- chunk: 5/11

```
(self, record: LogRecord) -> None: ...
    def format(self, record: LogRecord) -> str: ...
    def emit(self, record: LogRecord) -> None: ...

class Formatter:
    converter: Callable[[Optional[float]], struct_time]
    _fmt: Optional[str]
    datefmt: Optional[str]
    if sys.version_info >= (3,):
        _style: PercentStyle
        default_time_format: str
        default_msec_format: str

    if sys.version_info >= (3, 8):
        def __init__(
            self, fmt: Optional[str] = ..., datefmt: Optional[str] = ..., style: str = ..., validate: bool = ...
        ) -> None: ...
    elif sys.version_info >= (3,):
        def __init__(self, fmt: Optional[str] = ..., datefmt: Optional[str] = ..., style: str = ...) -> None: ...
    else:
        def __init__(self, fmt: Optional[str] = ..., datefmt: Optional[str] = ...) -> None: ...
    def format(self, record: LogRecord) -> str: ...
    def formatTime(self, record: LogRecord, datefmt: Optional[str] = ...) -> str: ...
    def formatException(self, ei: _SysExcInfoType) -> str: ...
    if sys.version_info >= (3,):
        def formatMessage(self, record: LogRecord) -> str: ...  # undocumented
        def formatStack(self, stack_info: str) -> str: ...

class Filter:
    def __init__(self, name: str = ...) -> None: ...
    def filter(self, record: LogRecord) -> bool: ...

class LogRecord:
    args: _ArgsType
    asctime: str
    created: int
    exc_info: Optional[_SysExcInfoType]
    exc_text: Optional[str]
    filename: str
    funcName: str
    levelname: str
    levelno: int
    lineno: int
    module: str
    msecs: int
    message: str
    msg: str
    name: str
    pathname: str
    process: int
    processName: str
    relativeCreated: int
    if sys.version_info >= (3,):
        stack_info: Optional[str]
    thread: int
    threadName: str
    if sys.version_info >= (3,):
        def __init__(
            self,
            name: str,
            level: int,
            pathname: str,
            lineno: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_SysExcInfoType],
            func: Optional[str] = ...,
            sinfo: Optional[str] = ...,
        ) -> None: ...
    else:
        def __init__(
            self,
            name: str,
            level: int,
            pathname: str,
            lineno: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_SysExcInfoType],
            func: Optional[str] = ...,
        ) -> None: ...
    def getMessage(self) -> str: ...

class LoggerAdapter:
    logger: Logger
    extra: Mapping[str, Any]
    def __init__(self, logger: Logger, extra: Mapping[str, Any]) -> None: ...
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> Tuple[Any, MutableMapping[str, Any]]: ...
    if sys.version_info >= (3, 8):
        def debug(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
```
