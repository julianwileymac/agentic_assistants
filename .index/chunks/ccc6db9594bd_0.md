# Chunk: ccc6db9594bd_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/logging/__init__.pyi`
- lines: 1-107
- chunk: 1/11

```
import sys
import threading
from _typeshed import StrPath
from string import Template
from time import struct_time
from types import FrameType, TracebackType
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Text,
    Tuple,
    Union,
    overload,
)

_SysExcInfoType = Union[Tuple[type, BaseException, Optional[TracebackType]], Tuple[None, None, None]]
if sys.version_info >= (3, 5):
    _ExcInfoType = Union[None, bool, _SysExcInfoType, BaseException]
else:
    _ExcInfoType = Union[None, bool, _SysExcInfoType]
_ArgsType = Union[Tuple[Any, ...], Mapping[str, Any]]
_FilterType = Union[Filter, Callable[[LogRecord], int]]
_Level = Union[int, Text]

raiseExceptions: bool
logThreads: bool
logMultiprocessing: bool
logProcesses: bool
_srcfile: Optional[str]

def currentframe() -> FrameType: ...

if sys.version_info >= (3,):
    _levelToName: Dict[int, str]
    _nameToLevel: Dict[str, int]
else:
    _levelNames: Dict[Union[int, str], Union[str, int]]  # Union[int:str, str:int]

class Filterer(object):
    filters: List[Filter]
    def __init__(self) -> None: ...
    def addFilter(self, filter: _FilterType) -> None: ...
    def removeFilter(self, filter: _FilterType) -> None: ...
    def filter(self, record: LogRecord) -> bool: ...

class Logger(Filterer):
    name: str
    level: int
    parent: Union[Logger, PlaceHolder]
    propagate: bool
    handlers: List[Handler]
    disabled: int
    def __init__(self, name: str, level: _Level = ...) -> None: ...
    def setLevel(self, level: _Level) -> None: ...
    def isEnabledFor(self, level: int) -> bool: ...
    def getEffectiveLevel(self) -> int: ...
    def getChild(self, suffix: str) -> Logger: ...
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
```
