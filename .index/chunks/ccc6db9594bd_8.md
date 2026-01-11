# Chunk: ccc6db9594bd_8

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 686-796
- chunk: 9/11

```
: _ExcInfoType = ...,
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
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def exception(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def log(
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
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def info(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def warning(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def warn(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def error(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def critical(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def exception(
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def log(
        level: int,
        msg: Any,
        *args: Any,
        exc_info: _ExcInfoType = ...,
        stack_info: bool = ...,
        extra: Optional[Dict[str, Any]] = ...,
        **kwargs: Any,
    ) -> None: ...

else:
    def debug(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def info(
        msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
    ) -> None: ...
    def warning(
```
