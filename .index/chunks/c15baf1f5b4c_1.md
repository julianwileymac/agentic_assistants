# Chunk: c15baf1f5b4c_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/_socket.pyi`
- lines: 150-271
- chunk: 2/3

```
ERV: int
NI_NAMEREQD: int
NI_NOFQDN: int
NI_NUMERICHOST: int
NI_NUMERICSERV: int
PACKET_BROADCAST: int
PACKET_FASTROUTE: int
PACKET_HOST: int
PACKET_LOOPBACK: int
PACKET_MULTICAST: int
PACKET_OTHERHOST: int
PACKET_OUTGOING: int
PF_PACKET: int
SHUT_RD: int
SHUT_RDWR: int
SHUT_WR: int
SOCK_DGRAM: int
SOCK_RAW: int
SOCK_RDM: int
SOCK_SEQPACKET: int
SOCK_STREAM: int
SOL_HCI: int
SOL_IP: int
SOL_SOCKET: int
SOL_TCP: int
SOL_TIPC: int
SOL_UDP: int
SOMAXCONN: int
SO_ACCEPTCONN: int
SO_BROADCAST: int
SO_DEBUG: int
SO_DONTROUTE: int
SO_ERROR: int
SO_KEEPALIVE: int
SO_LINGER: int
SO_OOBINLINE: int
SO_RCVBUF: int
SO_RCVLOWAT: int
SO_RCVTIMEO: int
SO_REUSEADDR: int
SO_REUSEPORT: int
SO_SNDBUF: int
SO_SNDLOWAT: int
SO_SNDTIMEO: int
SO_TYPE: int
SSL_ERROR_EOF: int
SSL_ERROR_INVALID_ERROR_CODE: int
SSL_ERROR_SSL: int
SSL_ERROR_SYSCALL: int
SSL_ERROR_WANT_CONNECT: int
SSL_ERROR_WANT_READ: int
SSL_ERROR_WANT_WRITE: int
SSL_ERROR_WANT_X509_LOOKUP: int
SSL_ERROR_ZERO_RETURN: int
TCP_CORK: int
TCP_DEFER_ACCEPT: int
TCP_INFO: int
TCP_KEEPCNT: int
TCP_KEEPIDLE: int
TCP_KEEPINTVL: int
TCP_LINGER2: int
TCP_MAXSEG: int
TCP_NODELAY: int
TCP_QUICKACK: int
TCP_SYNCNT: int
TCP_WINDOW_CLAMP: int
TIPC_ADDR_ID: int
TIPC_ADDR_NAME: int
TIPC_ADDR_NAMESEQ: int
TIPC_CFG_SRV: int
TIPC_CLUSTER_SCOPE: int
TIPC_CONN_TIMEOUT: int
TIPC_CRITICAL_IMPORTANCE: int
TIPC_DEST_DROPPABLE: int
TIPC_HIGH_IMPORTANCE: int
TIPC_IMPORTANCE: int
TIPC_LOW_IMPORTANCE: int
TIPC_MEDIUM_IMPORTANCE: int
TIPC_NODE_SCOPE: int
TIPC_PUBLISHED: int
TIPC_SRC_DROPPABLE: int
TIPC_SUBSCR_TIMEOUT: int
TIPC_SUB_CANCEL: int
TIPC_SUB_PORTS: int
TIPC_SUB_SERVICE: int
TIPC_TOP_SRV: int
TIPC_WAIT_FOREVER: int
TIPC_WITHDRAWN: int
TIPC_ZONE_SCOPE: int

# PyCapsule
CAPI: Any

has_ipv6: bool

class error(IOError): ...
class gaierror(error): ...
class timeout(error): ...

class SocketType(object):
    family: int
    type: int
    proto: int
    timeout: float
    def __init__(self, family: int = ..., type: int = ..., proto: int = ...) -> None: ...
    def accept(self) -> Tuple[SocketType, Tuple[Any, ...]]: ...
    def bind(self, address: Tuple[Any, ...]) -> None: ...
    def close(self) -> None: ...
    def connect(self, address: Tuple[Any, ...]) -> None: ...
    def connect_ex(self, address: Tuple[Any, ...]) -> int: ...
    def dup(self) -> SocketType: ...
    def fileno(self) -> int: ...
    def getpeername(self) -> Tuple[Any, ...]: ...
    def getsockname(self) -> Tuple[Any, ...]: ...
    def getsockopt(self, level: int, option: int, buffersize: int = ...) -> str: ...
    def gettimeout(self) -> float: ...
    def listen(self, backlog: int) -> None: ...
    def makefile(self, mode: str = ..., buffersize: int = ...) -> IO[Any]: ...
    def recv(self, buffersize: int, flags: int = ...) -> str: ...
    def recv_into(self, buffer: bytearray, nbytes: int = ..., flags: int = ...) -> int: ...
    def recvfrom(self, buffersize: int, flags: int = ...) -> Tuple[Any, ...]: ...
```
