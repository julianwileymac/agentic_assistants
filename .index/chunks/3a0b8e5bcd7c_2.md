# Chunk: 3a0b8e5bcd7c_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/xmlrpc/server.pyi`
- lines: 124-161
- chunk: 3/3

```
oding: Optional[str] = ..., use_builtin_types: bool = ...) -> None: ...
    def handle_xmlrpc(self, request_text: str) -> None: ...
    def handle_get(self) -> None: ...
    def handle_request(self, request_text: Optional[str] = ...) -> None: ...

class ServerHTMLDoc(pydoc.HTMLDoc):  # undocumented
    def docroutine(self, object: object, name: str, mod: Optional[str] = ..., funcs: Mapping[str, str] = ..., classes: Mapping[str, str] = ..., methods: Mapping[str, str] = ..., cl: Optional[type] = ...) -> str: ...  # type: ignore
    def docserver(self, server_name: str, package_documentation: str, methods: Dict[str, str]) -> str: ...

class XMLRPCDocGenerator:  # undocumented

    server_name: str
    server_documentation: str
    server_title: str
    def __init__(self) -> None: ...
    def set_server_title(self, server_title: str) -> None: ...
    def set_server_name(self, server_name: str) -> None: ...
    def set_server_documentation(self, server_documentation: str) -> None: ...
    def generate_html_documentation(self) -> str: ...

class DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    def do_GET(self) -> None: ...

class DocXMLRPCServer(SimpleXMLRPCServer, XMLRPCDocGenerator):
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

class DocCGIXMLRPCRequestHandler(CGIXMLRPCRequestHandler, XMLRPCDocGenerator):
    def __init__(self) -> None: ...
```
