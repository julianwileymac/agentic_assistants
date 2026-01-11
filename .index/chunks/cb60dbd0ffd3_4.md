# Chunk: cb60dbd0ffd3_4

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/socket.pyi`
- lines: 479-606
- chunk: 5/9

```
TLINK_SKIP: int
    NETLINK_TAPBASE: int
    NETLINK_TCPDIAG: int
    NETLINK_USERSOCK: int
    NETLINK_W1: int
    NETLINK_XFRM: int

if sys.platform != "win32" and sys.platform != "darwin":
    # Linux and some BSD support is explicit in the docs
    # Windows and macOS do not support in practice
    AF_BLUETOOTH: AddressFamily
    BTPROTO_HCI: int
    BTPROTO_L2CAP: int
    BTPROTO_RFCOMM: int
    BTPROTO_SCO: int  # not in FreeBSD

    BDADDR_ANY: str
    BDADDR_LOCAL: str

    HCI_FILTER: int  # not in NetBSD or DragonFlyBSD
    # not in FreeBSD, NetBSD, or DragonFlyBSD
    HCI_TIME_STAMP: int
    HCI_DATA_DIR: int

if sys.platform == "darwin":
    # PF_SYSTEM is defined by macOS
    PF_SYSTEM: int
    SYSPROTO_CONTROL: int

# enum versions of above flags
if sys.version_info >= (3, 4):
    from enum import IntEnum
    class AddressFamily(IntEnum):
        AF_UNIX: int
        AF_INET: int
        AF_INET6: int
        AF_AAL5: int
        AF_ALG: int
        AF_APPLETALK: int
        AF_ASH: int
        AF_ATMPVC: int
        AF_ATMSVC: int
        AF_AX25: int
        AF_BLUETOOTH: int
        AF_BRIDGE: int
        AF_CAN: int
        AF_DECnet: int
        AF_ECONET: int
        AF_IPX: int
        AF_IRDA: int
        AF_KEY: int
        AF_LINK: int
        AF_LLC: int
        AF_NETBEUI: int
        AF_NETLINK: int
        AF_NETROM: int
        AF_PACKET: int
        AF_PPPOX: int
        AF_QIPCRTR: int
        AF_RDS: int
        AF_ROSE: int
        AF_ROUTE: int
        AF_SECURITY: int
        AF_SNA: int
        AF_SYSTEM: int
        AF_TIPC: int
        AF_UNSPEC: int
        AF_VSOCK: int
        AF_WANPIPE: int
        AF_X25: int
    class SocketKind(IntEnum):
        SOCK_STREAM: int
        SOCK_DGRAM: int
        SOCK_RAW: int
        SOCK_RDM: int
        SOCK_SEQPACKET: int
        SOCK_CLOEXEC: int
        SOCK_NONBLOCK: int

else:
    AddressFamily = int
    SocketKind = int

if sys.version_info >= (3, 6):
    from enum import IntFlag
    class AddressInfo(IntFlag):
        AI_ADDRCONFIG: int
        AI_ALL: int
        AI_CANONNAME: int
        AI_NUMERICHOST: int
        AI_NUMERICSERV: int
        AI_PASSIVE: int
        AI_V4MAPPED: int
    class MsgFlag(IntFlag):
        MSG_CTRUNC: int
        MSG_DONTROUTE: int
        MSG_DONTWAIT: int
        MSG_EOR: int
        MSG_OOB: int
        MSG_PEEK: int
        MSG_TRUNC: int
        MSG_WAITALL: int

else:
    AddressInfo = int
    MsgFlag = int

# ----- Exceptions -----

if sys.version_info < (3,):
    class error(IOError): ...

else:
    error = OSError

class herror(error):
    def __init__(self, herror: int = ..., string: str = ...) -> None: ...

class gaierror(error):
    def __init__(self, error: int = ..., string: str = ...) -> None: ...

class timeout(error):
    def __init__(self, error: int = ..., string: str = ...) -> None: ...

# ----- Classes -----

# Addresses can be either tuples of varying lengths (AF_INET, AF_INET6,
```
