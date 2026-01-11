# Chunk: b7f6c5cafaeb_1

- source: `.venv-lab/Lib/site-packages/zmq/backend/__init__.pyi`
- lines: 98-124
- chunk: 2/2

```
s | str) -> None: ...
    def socket(self, socket_type: int) -> Socket: ...
    def term(self) -> None: ...

IPC_PATH_MAX_LEN: int
PYZMQ_DRAFT_API: bool

def has(capability: str) -> bool: ...
def curve_keypair() -> tuple[bytes, bytes]: ...
def curve_public(secret_key: bytes) -> bytes: ...
def strerror(errno: int | None = ...) -> str: ...
def zmq_errno() -> int: ...
def zmq_version() -> str: ...
def zmq_version_info() -> tuple[int, int, int]: ...
def zmq_poll(
    sockets: list[Any], timeout: int | None = ...
) -> list[tuple[Socket, int]]: ...
def proxy(frontend: Socket, backend: Socket, capture: Socket | None = None) -> int: ...
def proxy_steerable(
    frontend: Socket,
    backend: Socket,
    capture: Socket | None = ...,
    control: Socket | None = ...,
) -> int: ...

monitored_queue = Callable | None
```
