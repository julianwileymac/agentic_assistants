# Chunk: ccc6db9594bd_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 187-275
- chunk: 3/11

```
          self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def error(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def critical(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        fatal = critical
        def log(
            self,
            level: int,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def exception(
            self,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            stack_info: bool = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def _log(
            self,
            level: int,
            msg: Any,
            args: _ArgsType,
            exc_info: Optional[_ExcInfoType] = ...,
            extra: Optional[Dict[str, Any]] = ...,
            stack_info: bool = ...,
        ) -> None: ...  # undocumented
    else:
        def debug(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def info(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def warning(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        warn = warning
        def error(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def critical(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        fatal = critical
        def log(
            self,
            level: int,
            msg: Any,
            *args: Any,
            exc_info: _ExcInfoType = ...,
            extra: Optional[Dict[str, Any]] = ...,
            **kwargs: Any,
        ) -> None: ...
        def exception(
            self, msg: Any, *args: Any, exc_info: _ExcInfoType = ..., extra: Optional[Dict[str, Any]] = ..., **kwargs: Any
        ) -> None: ...
        def _log(
            self,
            level: int,
```
