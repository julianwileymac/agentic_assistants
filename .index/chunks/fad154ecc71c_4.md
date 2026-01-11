# Chunk: fad154ecc71c_4

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/request.pyi`
- lines: 242-297
- chunk: 5/6

```
rt: int, dirs: str, timeout: float
    ) -> ftpwrapper: ...  # undocumented

class UnknownHandler(BaseHandler):
    def unknown_open(self, req: Request) -> NoReturn: ...

class HTTPErrorProcessor(BaseHandler):
    def http_response(self, request: Request, response: HTTPResponse) -> _UrlopenRet: ...
    def https_response(self, request: Request, response: HTTPResponse) -> _UrlopenRet: ...

def urlretrieve(
    url: str,
    filename: Optional[Union[str, os.PathLike[Any]]] = ...,
    reporthook: Optional[Callable[[int, int, int], None]] = ...,
    data: Optional[bytes] = ...,
) -> Tuple[str, HTTPMessage]: ...
def urlcleanup() -> None: ...

class URLopener:
    version: ClassVar[str]
    def __init__(self, proxies: Optional[Dict[str, str]] = ..., **x509: str) -> None: ...
    def open(self, fullurl: str, data: Optional[bytes] = ...) -> _UrlopenRet: ...
    def open_unknown(self, fullurl: str, data: Optional[bytes] = ...) -> _UrlopenRet: ...
    def retrieve(
        self,
        url: str,
        filename: Optional[str] = ...,
        reporthook: Optional[Callable[[int, int, int], None]] = ...,
        data: Optional[bytes] = ...,
    ) -> Tuple[str, Optional[Message]]: ...
    def addheader(self, *args: Tuple[str, str]) -> None: ...  # undocumented
    def cleanup(self) -> None: ...  # undocumented
    def close(self) -> None: ...  # undocumented
    def http_error(
        self, url: str, fp: IO[bytes], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> _UrlopenRet: ...  # undocumented
    def http_error_default(
        self, url: str, fp: IO[bytes], errcode: int, errmsg: str, headers: Mapping[str, str]
    ) -> _UrlopenRet: ...  # undocumented
    def open_data(self, url: str, data: Optional[bytes] = ...) -> addinfourl: ...  # undocumented
    def open_file(self, url: str) -> addinfourl: ...  # undocumented
    def open_ftp(self, url: str) -> addinfourl: ...  # undocumented
    def open_http(self, url: str, data: Optional[bytes] = ...) -> _UrlopenRet: ...  # undocumented
    def open_https(self, url: str, data: Optional[bytes] = ...) -> _UrlopenRet: ...  # undocumented
    def open_local_file(self, url: str) -> addinfourl: ...  # undocumented
    def open_unknown_proxy(self, proxy: str, fullurl: str, data: Optional[bytes] = ...) -> None: ...  # undocumented

class FancyURLopener(URLopener):
    def prompt_user_passwd(self, host: str, realm: str) -> Tuple[str, str]: ...
    def get_user_passwd(self, host: str, realm: str, clear_cache: int = ...) -> Tuple[str, str]: ...  # undocumented
    def http_error_301(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> Optional[Union[_UrlopenRet, addinfourl]]: ...  # undocumented
    def http_error_302(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
```
