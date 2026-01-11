# Chunk: ccc6db9594bd_7

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 599-697
- chunk: 8/11

```
y, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def exception(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def critical(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def log(
            self,
            level: int,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
    def isEnabledFor(self, level: int) -> bool: ...
    if sys.version_info >= (3,):
        def getEffectiveLevel(self) -> int: ...
        def setLevel(self, level: Union[int, str]) -> None: ...
        def hasHandlers(self) -> bool: ...
    if sys.version_info >= (3, 6):
        def _log(
            self,
            level: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_ExcInfoType] = ...,
            extra: Optional[Dict[str, Any]] = ...,
            stack_info: bool = ...,
        ) -> None: ...  # undocumented

if sys.version_info >= (3,):
    def getLogger(name: Optional[str] = ...) -> Logger: ...

else:
    @overload
    def getLogger() -> Logger: ...
    @overload
    def getLogger(name: Union[Text, str]) -> Logger: ...

def getLoggerClass() -> type: ...

if sys.version_info >= (3,):
    def getLogRecordFactory() -> Callable[..., LogRecord]: ...

if sys.version_info >= (3, 8):
    def debug(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def info(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def warning(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def warn(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def error(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def critical(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
```
