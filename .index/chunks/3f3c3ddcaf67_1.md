# Chunk: 3f3c3ddcaf67_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/httplib.pyi`
- lines: 75-205
- chunk: 2/3

```
nal[Any] = ...): ...
    def getfile(self): ...
    file: Any
    headers: Any
    def getreply(self, buffering: bool = ...): ...
    def close(self): ...

class HTTPSConnection(HTTPConnection):
    default_port: Any
    key_file: Any
    cert_file: Any
    def __init__(
        self,
        host,
        port: Optional[Any] = ...,
        key_file: Optional[Any] = ...,
        cert_file: Optional[Any] = ...,
        strict: Optional[Any] = ...,
        timeout=...,
        source_address: Optional[Any] = ...,
        context: Optional[Any] = ...,
    ) -> None: ...
    sock: Any
    def connect(self): ...

class HTTPS(HTTP):
    key_file: Any
    cert_file: Any
    def __init__(
        self,
        host: str = ...,
        port: Optional[Any] = ...,
        key_file: Optional[Any] = ...,
        cert_file: Optional[Any] = ...,
        strict: Optional[Any] = ...,
        context: Optional[Any] = ...,
    ) -> None: ...

class HTTPException(Exception): ...
class NotConnected(HTTPException): ...
class InvalidURL(HTTPException): ...

class UnknownProtocol(HTTPException):
    args: Any
    version: Any
    def __init__(self, version) -> None: ...

class UnknownTransferEncoding(HTTPException): ...
class UnimplementedFileMode(HTTPException): ...

class IncompleteRead(HTTPException):
    args: Any
    partial: Any
    expected: Any
    def __init__(self, partial, expected: Optional[Any] = ...) -> None: ...

class ImproperConnectionState(HTTPException): ...
class CannotSendRequest(ImproperConnectionState): ...
class CannotSendHeader(ImproperConnectionState): ...
class ResponseNotReady(ImproperConnectionState): ...

class BadStatusLine(HTTPException):
    args: Any
    line: Any
    def __init__(self, line) -> None: ...

class LineTooLong(HTTPException):
    def __init__(self, line_type) -> None: ...

error: Any

class LineAndFileWrapper:
    def __init__(self, line, file) -> None: ...
    def __getattr__(self, attr): ...
    def read(self, amt: Optional[Any] = ...): ...
    def readline(self): ...
    def readlines(self, size: Optional[Any] = ...): ...

# Constants

responses: Dict[int, str]

HTTP_PORT: int
HTTPS_PORT: int

# status codes
# informational
CONTINUE: int
SWITCHING_PROTOCOLS: int
PROCESSING: int

# successful
OK: int
CREATED: int
ACCEPTED: int
NON_AUTHORITATIVE_INFORMATION: int
NO_CONTENT: int
RESET_CONTENT: int
PARTIAL_CONTENT: int
MULTI_STATUS: int
IM_USED: int

# redirection
MULTIPLE_CHOICES: int
MOVED_PERMANENTLY: int
FOUND: int
SEE_OTHER: int
NOT_MODIFIED: int
USE_PROXY: int
TEMPORARY_REDIRECT: int

# client error
BAD_REQUEST: int
UNAUTHORIZED: int
PAYMENT_REQUIRED: int
FORBIDDEN: int
NOT_FOUND: int
METHOD_NOT_ALLOWED: int
NOT_ACCEPTABLE: int
PROXY_AUTHENTICATION_REQUIRED: int
REQUEST_TIMEOUT: int
CONFLICT: int
GONE: int
LENGTH_REQUIRED: int
PRECONDITION_FAILED: int
REQUEST_ENTITY_TOO_LARGE: int
REQUEST_URI_TOO_LONG: int
UNSUPPORTED_MEDIA_TYPE: int
REQUESTED_RANGE_NOT_SATISFIABLE: int
EXPECTATION_FAILED: int
```
