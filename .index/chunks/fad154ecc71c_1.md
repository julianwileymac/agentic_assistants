# Chunk: fad154ecc71c_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/request.pyi`
- lines: 89-146
- chunk: 2/6

```
] = ..., timeout: Optional[float] = ...) -> _UrlopenRet: ...
    def error(self, proto: str, *args: Any) -> _UrlopenRet: ...
    def close(self) -> None: ...

class BaseHandler:
    handler_order: ClassVar[int]
    parent: OpenerDirector
    def add_parent(self, parent: OpenerDirector) -> None: ...
    def close(self) -> None: ...
    def http_error_nnn(self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]) -> _UrlopenRet: ...

class HTTPDefaultErrorHandler(BaseHandler):
    def http_error_default(
        self, req: Request, fp: IO[bytes], code: int, msg: str, hdrs: Mapping[str, str]
    ) -> HTTPError: ...  # undocumented

class HTTPRedirectHandler(BaseHandler):
    max_redirections: ClassVar[int]  # undocumented
    max_repeats: ClassVar[int]  # undocumented
    inf_msg: ClassVar[str]  # undocumented
    def redirect_request(
        self, req: Request, fp: IO[str], code: int, msg: str, headers: Mapping[str, str], newurl: str
    ) -> Optional[Request]: ...
    def http_error_301(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...
    def http_error_302(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...
    def http_error_303(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...
    def http_error_307(
        self, req: Request, fp: IO[str], code: int, msg: int, headers: Mapping[str, str]
    ) -> Optional[_UrlopenRet]: ...

class HTTPCookieProcessor(BaseHandler):
    cookiejar: CookieJar
    def __init__(self, cookiejar: Optional[CookieJar] = ...) -> None: ...
    def http_request(self, request: Request) -> Request: ...  # undocumented
    def http_response(self, request: Request, response: HTTPResponse) -> HTTPResponse: ...  # undocumented
    def https_request(self, request: Request) -> Request: ...  # undocumented
    def https_response(self, request: Request, response: HTTPResponse) -> HTTPResponse: ...  # undocumented

class ProxyHandler(BaseHandler):
    def __init__(self, proxies: Optional[Dict[str, str]] = ...) -> None: ...
    def proxy_open(self, req: Request, proxy: str, type: str) -> Optional[_UrlopenRet]: ...  # undocumented
    # TODO add a method for every (common) proxy protocol

class HTTPPasswordMgr:
    def add_password(self, realm: str, uri: Union[str, Sequence[str]], user: str, passwd: str) -> None: ...
    def find_user_password(self, realm: str, authuri: str) -> Tuple[Optional[str], Optional[str]]: ...
    def is_suburi(self, base: str, test: str) -> bool: ...  # undocumented
    def reduce_uri(self, uri: str, default_port: bool = ...) -> str: ...  # undocumented

class HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):
    def add_password(self, realm: Optional[str], uri: Union[str, Sequence[str]], user: str, passwd: str) -> None: ...
```
