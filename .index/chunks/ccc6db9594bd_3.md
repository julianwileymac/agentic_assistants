# Chunk: ccc6db9594bd_3

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 266-353
- chunk: 4/11

```
ct[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def exception(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def _log(
            self,
            level: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_ExcInfoType] = ...,
            extra: Optional[Dict[str, Any]] = ...,
        ) -> None: ...  # undocumented
    def filter(self, record: LogRecord) -> bool: ...
    def addHandler(self, hdlr: Handler) -> None: ...
    def removeHandler(self, hdlr: Handler) -> None: ...
    if sys.version_info >= (3, 8):
        def findCaller(self, stack_info: bool = ..., stacklevel: int = ...) -> Tuple[str, int, str, Optional[str]]: ...
    elif sys.version_info >= (3,):
        def findCaller(self, stack_info: bool = ...) -> Tuple[str, int, str, Optional[str]]: ...
    else:
        def findCaller(self) -> Tuple[str, int, str]: ...
    def handle(self, record: LogRecord) -> None: ...
    if sys.version_info >= (3,):
        def makeRecord(
            self,
            name: str,
            level: int,
            fn: str,
            lno: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_SysExcInfoType],
            func: Optional[str] = ...,
            extra: Optional[Mapping[str, Any]] = ...,
            sinfo: Optional[str] = ...,
        ) -> LogRecord: ...
    else:
        def makeRecord(
            self,
            name: str,
            level: int,
            fn: str,
            lno: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_SysExcInfoType],
            func: Optional[str] = ...,
            extra: Optional[Mapping[str, Any]] = ...,
        ) -> LogRecord: ...
    if sys.version_info >= (3,):
        def hasHandlers(self) -> bool: ...

CRITICAL: int
FATAL: int
ERROR: int
WARNING: int
WARN: int
INFO: int
DEBUG: int
NOTSET: int

class Handler(Filterer):
    level: int  # undocumented
    formatter: Optional[Formatter]  # undocumented
    lock: Optional[threading.Lock]  # undocumented
    name: Optional[str]  # undocumented
    def __init__(self, level: _Level = ...) -> None: ...
    def createLock(self) -> None: ...
    def acquire(self) -> None: ...
    def release(self) -> None: ...
    def setLevel(self, level: _Level) -> None: ...
    def setFormatter(self, fmt: Formatter) -> None: ...
    def filter(self, record: LogRecord) -> bool: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...
    def handle(self, record: LogRecord) -> None: ...
    def handleError(self, record: LogRecord) -> None: ...
    def format(self, record: LogRecord) -> str: ...
    def emit(self, record: LogRecord) -> None: ...

class Formatter:
    converter: Callable[[Optional[float]], struct_time]
    _fmt: Optional[str]
    datefmt: Optional[str]
    if sys.version_info >= (3,):
```
