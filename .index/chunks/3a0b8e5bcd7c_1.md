# Chunk: 3a0b8e5bcd7c_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/xmlrpc/server.pyi`
- lines: 64-130
- chunk: 2/3

```
 ...  # undocumented
    def system_methodSignature(self, method_name: str) -> str: ...  # undocumented
    def system_methodHelp(self, method_name: str) -> str: ...  # undocumented
    def system_multicall(self, call_list: List[Dict[str, _Marshallable]]) -> List[_Marshallable]: ...  # undocumented
    def _dispatch(self, method: str, params: Iterable[_Marshallable]) -> _Marshallable: ...  # undocumented

class SimpleXMLRPCRequestHandler(http.server.BaseHTTPRequestHandler):

    rpc_paths: Tuple[str, str] = ...
    encode_threshold: int = ...  # undocumented
    aepattern: Pattern[str]  # undocumented
    def accept_encodings(self) -> Dict[str, float]: ...
    def is_rpc_path_valid(self) -> bool: ...
    def do_POST(self) -> None: ...
    def decode_request_content(self, data: bytes) -> Optional[bytes]: ...
    def report_404(self) -> None: ...
    def log_request(self, code: Union[int, str] = ..., size: Union[int, str] = ...) -> None: ...

class SimpleXMLRPCServer(socketserver.TCPServer, SimpleXMLRPCDispatcher):

    allow_reuse_address: bool = ...
    _send_traceback_handler: bool = ...
    def __init__(
        self,
        addr: Tuple[str, int],
        requestHandler: Type[SimpleXMLRPCRequestHandler] = ...,
        logRequests: bool = ...,
        allow_none: bool = ...,
        encoding: Optional[str] = ...,
        bind_and_activate: bool = ...,
        use_builtin_types: bool = ...,
    ) -> None: ...

class MultiPathXMLRPCServer(SimpleXMLRPCServer):  # undocumented

    dispatchers: Dict[str, SimpleXMLRPCDispatcher]
    allow_none: bool
    encoding: str
    def __init__(
        self,
        addr: Tuple[str, int],
        requestHandler: Type[SimpleXMLRPCRequestHandler] = ...,
        logRequests: bool = ...,
        allow_none: bool = ...,
        encoding: Optional[str] = ...,
        bind_and_activate: bool = ...,
        use_builtin_types: bool = ...,
    ) -> None: ...
    def add_dispatcher(self, path: str, dispatcher: SimpleXMLRPCDispatcher) -> SimpleXMLRPCDispatcher: ...
    def get_dispatcher(self, path: str) -> SimpleXMLRPCDispatcher: ...
    def _marshaled_dispatch(
        self,
        data: str,
        dispatch_method: Optional[
            Callable[[Optional[str], Tuple[_Marshallable, ...]], Union[Fault, Tuple[_Marshallable, ...]]]
        ] = ...,
        path: Optional[Any] = ...,
    ) -> str: ...

class CGIXMLRPCRequestHandler(SimpleXMLRPCDispatcher):
    def __init__(self, allow_none: bool = ..., encoding: Optional[str] = ..., use_builtin_types: bool = ...) -> None: ...
    def handle_xmlrpc(self, request_text: str) -> None: ...
    def handle_get(self) -> None: ...
    def handle_request(self, request_text: Optional[str] = ...) -> None: ...

class ServerHTMLDoc(pydoc.HTMLDoc):  # undocumented
```
