# Chunk: ca3ff15f6aaf_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/parse.pyi`
- lines: 1-102
- chunk: 1/2

```
import sys
from typing import Any, AnyStr, Callable, Dict, Generic, List, Mapping, NamedTuple, Optional, Sequence, Tuple, Union, overload

if sys.version_info >= (3, 9):
    from types import GenericAlias

_Str = Union[bytes, str]

uses_relative: List[str]
uses_netloc: List[str]
uses_params: List[str]
non_hierarchical: List[str]
uses_query: List[str]
uses_fragment: List[str]
scheme_chars: str
MAX_CACHE_SIZE: int

class _ResultMixinBase(Generic[AnyStr]):
    def geturl(self) -> AnyStr: ...

class _ResultMixinStr(_ResultMixinBase[str]):
    def encode(self, encoding: str = ..., errors: str = ...) -> _ResultMixinBytes: ...

class _ResultMixinBytes(_ResultMixinBase[str]):
    def decode(self, encoding: str = ..., errors: str = ...) -> _ResultMixinStr: ...

class _NetlocResultMixinBase(Generic[AnyStr]):
    username: Optional[AnyStr]
    password: Optional[AnyStr]
    hostname: Optional[AnyStr]
    port: Optional[int]
    if sys.version_info >= (3, 9):
        def __class_getitem__(cls, item: Any) -> GenericAlias: ...

class _NetlocResultMixinStr(_NetlocResultMixinBase[str], _ResultMixinStr): ...
class _NetlocResultMixinBytes(_NetlocResultMixinBase[bytes], _ResultMixinBytes): ...

class _DefragResultBase(Tuple[Any, ...], Generic[AnyStr]):
    url: AnyStr
    fragment: AnyStr

class _SplitResultBase(NamedTuple):
    scheme: str
    netloc: str
    path: str
    query: str
    fragment: str

class _SplitResultBytesBase(NamedTuple):
    scheme: bytes
    netloc: bytes
    path: bytes
    query: bytes
    fragment: bytes

class _ParseResultBase(NamedTuple):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

class _ParseResultBytesBase(NamedTuple):
    scheme: bytes
    netloc: bytes
    path: bytes
    params: bytes
    query: bytes
    fragment: bytes

# Structured result objects for string data
class DefragResult(_DefragResultBase[str], _ResultMixinStr): ...
class SplitResult(_SplitResultBase, _NetlocResultMixinStr): ...
class ParseResult(_ParseResultBase, _NetlocResultMixinStr): ...

# Structured result objects for bytes data
class DefragResultBytes(_DefragResultBase[bytes], _ResultMixinBytes): ...
class SplitResultBytes(_SplitResultBytesBase, _NetlocResultMixinBytes): ...
class ParseResultBytes(_ParseResultBytesBase, _NetlocResultMixinBytes): ...

if sys.version_info >= (3, 8):
    def parse_qs(
        qs: Optional[AnyStr],
        keep_blank_values: bool = ...,
        strict_parsing: bool = ...,
        encoding: str = ...,
        errors: str = ...,
        max_num_fields: Optional[int] = ...,
    ) -> Dict[AnyStr, List[AnyStr]]: ...
    def parse_qsl(
        qs: Optional[AnyStr],
        keep_blank_values: bool = ...,
        strict_parsing: bool = ...,
        encoding: str = ...,
        errors: str = ...,
        max_num_fields: Optional[int] = ...,
    ) -> List[Tuple[AnyStr, AnyStr]]: ...

else:
    def parse_qs(
```
