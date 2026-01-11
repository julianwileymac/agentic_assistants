# Chunk: fad154ecc71c_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/request.pyi`
- lines: 1-97
- chunk: 1/6

```
import os
import ssl
from email.message import Message
from http.client import HTTPMessage, HTTPResponse, _HTTPConnectionProtocol
from http.cookiejar import CookieJar
from typing import (
    IO,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Mapping,
    NoReturn,
    Optional,
    Pattern,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)
from urllib.error import HTTPError
from urllib.response import addinfourl

_T = TypeVar("_T")
_UrlopenRet = Any

def urlopen(
    url: Union[str, Request],
    data: Optional[bytes] = ...,
    timeout: Optional[float] = ...,
    *,
    cafile: Optional[str] = ...,
    capath: Optional[str] = ...,
    cadefault: bool = ...,
    context: Optional[ssl.SSLContext] = ...,
) -> _UrlopenRet: ...
def install_opener(opener: OpenerDirector) -> None: ...
def build_opener(*handlers: Union[BaseHandler, Callable[[], BaseHandler]]) -> OpenerDirector: ...
def url2pathname(pathname: str) -> str: ...
def pathname2url(pathname: str) -> str: ...
def getproxies() -> Dict[str, str]: ...
def parse_http_list(s: str) -> List[str]: ...
def parse_keqv_list(l: List[str]) -> Dict[str, str]: ...
def proxy_bypass(host: str) -> Any: ...  # Undocumented

class Request:
    @property
    def full_url(self) -> str: ...
    @full_url.setter
    def full_url(self, value: str) -> None: ...
    @full_url.deleter
    def full_url(self) -> None: ...
    type: str
    host: str
    origin_req_host: str
    selector: str
    data: Optional[bytes]
    headers: Dict[str, str]
    unverifiable: bool
    method: Optional[str]
    def __init__(
        self,
        url: str,
        data: Optional[bytes] = ...,
        headers: Dict[str, str] = ...,
        origin_req_host: Optional[str] = ...,
        unverifiable: bool = ...,
        method: Optional[str] = ...,
    ) -> None: ...
    def get_method(self) -> str: ...
    def add_header(self, key: str, val: str) -> None: ...
    def add_unredirected_header(self, key: str, val: str) -> None: ...
    def has_header(self, header_name: str) -> bool: ...
    def remove_header(self, header_name: str) -> None: ...
    def get_full_url(self) -> str: ...
    def set_proxy(self, host: str, type: str) -> None: ...
    @overload
    def get_header(self, header_name: str) -> Optional[str]: ...
    @overload
    def get_header(self, header_name: str, default: _T) -> Union[str, _T]: ...
    def header_items(self) -> List[Tuple[str, str]]: ...
    def has_proxy(self) -> bool: ...

class OpenerDirector:
    addheaders: List[Tuple[str, str]]
    def add_handler(self, handler: BaseHandler) -> None: ...
    def open(self, fullurl: Union[str, Request], data: Optional[bytes] = ..., timeout: Optional[float] = ...) -> _UrlopenRet: ...
    def error(self, proto: str, *args: Any) -> _UrlopenRet: ...
    def close(self) -> None: ...

class BaseHandler:
    handler_order: ClassVar[int]
    parent: OpenerDirector
    def add_parent(self, parent: OpenerDirector) -> None: ...
```
