# Chunk: ccc6db9594bd_5

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 430-528
- chunk: 6/11

```
ping[str, Any]) -> None: ...
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> Tuple[Any, MutableMapping[str, Any]]: ...
    if sys.version_info >= (3, 8):
        def debug(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def info(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def warning(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def warn(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def error(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def exception(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def critical(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def log(
            self,
            level: int,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            stacklevel: int = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
    elif sys.version_info >= (3,):
        def debug(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def info(
            self,
            msg: Any,
            *args: Any,
```
