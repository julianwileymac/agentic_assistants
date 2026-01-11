# Chunk: ccc6db9594bd_9

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 789-879
- chunk: 10/11

```
bug(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def info(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def warning(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    warn = warning
    def error(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def critical(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def exception(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def log(
        level: int, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...

fatal = critical

if sys.version_info >= (3, 7):
    def disable(level: int = ...) -> None: ...

else:
    def disable(level: int) -> None: ...

def addLevelName(level: int, levelName: str) -> None: ...
def getLevelName(level: Union[int, str]) -> Any: ...
def makeLogRecord(dict: Mapping[str, Any]) -> LogRecord: ...

if sys.version_info >= (3, 8):
    def basicConfig(
        *,
        filename: Optional[StrPath] = ...,
        filemode: str = ...,
        format: str = ...,
        datefmt: Optional[str] = ...,
        style: str = ...,
        level: Optional[_Level] = ...,
        stream: Optional[IO[str]] = ...,
        handlers: Optional[Iterable[Handler]] = ...,
        force: bool = ...,
    ) -> None: ...

elif sys.version_info >= (3,):
    def basicConfig(
        *,
        filename: Optional[StrPath] = ...,
        filemode: str = ...,
        format: str = ...,
        datefmt: Optional[str] = ...,
        style: str = ...,
        level: Optional[_Level] = ...,
        stream: Optional[IO[str]] = ...,
        handlers: Optional[Iterable[Handler]] = ...,
    ) -> None: ...

else:
    @overload
    def basicConfig() -> None: ...
    @overload
    def basicConfig(
        *,
        filename: Optional[str] = ...,
        filemode: str = ...,
        format: str = ...,
        datefmt: Optional[str] = ...,
        level: Optional[_Level] = ...,
        stream: IO[str] = ...,
    ) -> None: ...

def shutdown(handlerList: Sequence[Any] = ...) -> None: ...  # handlerList is undocumented
def setLoggerClass(klass: type) -> None: ...
def captureWarnings(capture: bool) -> None: ...

if sys.version_info >= (3,):
    def setLogRecordFactory(factory: Callable[..., LogRecord]) -> None: ...

if sys.version_info >= (3,):
    lastResort: Optional[StreamHandler]

class StreamHandler(Handler):
    stream: IO[str]  # undocumented
    if sys.version_info >= (3, 2):
        terminator: str
```
