# Chunk: fad154ecc71c_3

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/request.pyi`
- lines: 184-250
- chunk: 4/6

```
le[Callable[[str], str], Callable[[str, str], str]]: ...
    def get_entity_digest(self, data: Optional[bytes], chal: Mapping[str, str]) -> Optional[str]: ...

class HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    auth_header: ClassVar[str]  # undocumented
    def http_error_401(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...

class ProxyDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    auth_header: ClassVar[str]  # undocumented
    def http_error_407(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...

class AbstractHTTPHandler(BaseHandler):  # undocumented
    def __init__(self, debuglevel: int = ...) -> None: ...
    def set_http_debuglevel(self, level: int) -> None: ...
    def do_request_(self, request: Request) -> Request: ...
    def do_open(self, http_class: _HTTPConnectionProtocol, req: Request, **http_conn_args: Any) -> HTTPResponse: ...

class HTTPHandler(AbstractHTTPHandler):
    def http_open(self, req: Request) -> HTTPResponse: ...
    def http_request(self, request: Request) -> Request: ...  # undocumented

class HTTPSHandler(AbstractHTTPHandler):
    def __init__(
        self, debuglevel: int = ..., context: Optional[ssl.SSLContext] = ..., check_hostname: Optional[bool] = ...
    ) -> None: ...
    def https_open(self, req: Request) -> HTTPResponse: ...
    def https_request(self, request: Request) -> Request: ...  # undocumented

class FileHandler(BaseHandler):
    names: ClassVar[Optional[Tuple[str, ...]]]  # undocumented
    def file_open(self, req: Request) -> addinfourl: ...
    def get_names(self) -> Tuple[str, ...]: ...  # undocumented
    def open_local_file(self, req: Request) -> addinfourl: ...  # undocumented

class DataHandler(BaseHandler):
    def data_open(self, req: Request) -> addinfourl: ...

class ftpwrapper:  # undocumented
    def __init__(
        self, user: str, passwd: str, host: str, port: int, dirs: str, timeout: Optional[float] = ..., persistent: bool = ...
    ) -> None: ...

class FTPHandler(BaseHandler):
    def ftp_open(self, req: Request) -> addinfourl: ...
    def connect_ftp(
        self, user: str, passwd: str, host: str, port: int, dirs: str, timeout: float
    ) -> ftpwrapper: ...  # undocumented

class CacheFTPHandler(FTPHandler):
    def setTimeout(self, t: float) -> None: ...
    def setMaxConns(self, m: int) -> None: ...
    def check_cache(self) -> None: ...  # undocumented
    def clear_cache(self) -> None: ...  # undocumented
    def connect_ftp(
        self, user: str, passwd: str, host: str, port: int, dirs: str, timeout: float
    ) -> ftpwrapper: ...  # undocumented

class UnknownHandler(BaseHandler):
    def unknown_open(self, req: Request) -> NoReturn: ...

class HTTPErrorProcessor(BaseHandler):
    def http_response(self, request: Request, response: HTTPResponse) -> _UrlopenRet: ...
```
