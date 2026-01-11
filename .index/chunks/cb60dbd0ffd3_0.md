# Chunk: cb60dbd0ffd3_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/socket.pyi`
- lines: 1-133
- chunk: 1/9

```
import sys
from typing import Any, BinaryIO, Iterable, List, Optional, Text, TextIO, Tuple, TypeVar, Union, overload
from typing_extensions import Literal

# ----- Constants -----
# Some socket families are listed in the "Socket families" section of the docs,
# but not the "Constants" section. These are listed at the end of the list of
# constants.
#
# Besides those and the first few constants listed, the constants are listed in
# documentation order.

# Constants defined by Python (i.e. not OS constants re-exported from C)
has_ipv6: bool
SocketType: Any
if sys.version_info >= (3,):
    SocketIO: Any

# Re-exported errno
EAGAIN: int
EBADF: int
EINTR: int
EWOULDBLOCK: int

# Constants re-exported from C

# Per socketmodule.c, only these three families are portable
AF_UNIX: AddressFamily
AF_INET: AddressFamily
AF_INET6: AddressFamily

SOCK_STREAM: SocketKind
SOCK_DGRAM: SocketKind
SOCK_RAW: SocketKind
SOCK_RDM: SocketKind
SOCK_SEQPACKET: SocketKind

if sys.platform == "linux" and sys.version_info >= (3,):
    SOCK_CLOEXEC: SocketKind
    SOCK_NONBLOCK: SocketKind

# Address families not mentioned in the docs
AF_AAL5: AddressFamily
AF_APPLETALK: AddressFamily
AF_ASH: AddressFamily
AF_ATMPVC: AddressFamily
AF_ATMSVC: AddressFamily
AF_AX25: AddressFamily
AF_BRIDGE: AddressFamily
AF_DECnet: AddressFamily
AF_ECONET: AddressFamily
AF_IPX: AddressFamily
AF_IRDA: AddressFamily
AF_KEY: AddressFamily
AF_LLC: AddressFamily
AF_NETBEUI: AddressFamily
AF_NETROM: AddressFamily
AF_PPPOX: AddressFamily
AF_ROSE: AddressFamily
AF_ROUTE: AddressFamily
AF_SECURITY: AddressFamily
AF_SNA: AddressFamily
AF_SYSTEM: AddressFamily
AF_UNSPEC: AddressFamily
AF_WANPIPE: AddressFamily
AF_X25: AddressFamily

# The "many constants" referenced by the docs
SOMAXCONN: int
AI_ADDRCONFIG: AddressInfo
AI_ALL: AddressInfo
AI_CANONNAME: AddressInfo
AI_DEFAULT: AddressInfo
AI_MASK: AddressInfo
AI_NUMERICHOST: AddressInfo
AI_NUMERICSERV: AddressInfo
AI_PASSIVE: AddressInfo
AI_V4MAPPED: AddressInfo
AI_V4MAPPED_CFG: AddressInfo
EAI_ADDRFAMILY: int
EAI_AGAIN: int
EAI_BADFLAGS: int
EAI_BADHINTS: int
EAI_FAIL: int
EAI_FAMILY: int
EAI_MAX: int
EAI_MEMORY: int
EAI_NODATA: int
EAI_NONAME: int
EAI_OVERFLOW: int
EAI_PROTOCOL: int
EAI_SERVICE: int
EAI_SOCKTYPE: int
EAI_SYSTEM: int
INADDR_ALLHOSTS_GROUP: int
INADDR_ANY: int
INADDR_BROADCAST: int
INADDR_LOOPBACK: int
INADDR_MAX_LOCAL_GROUP: int
INADDR_NONE: int
INADDR_UNSPEC_GROUP: int
IPPORT_RESERVED: int
IPPORT_USERRESERVED: int
IPPROTO_AH: int
IPPROTO_BIP: int
IPPROTO_DSTOPTS: int
IPPROTO_EGP: int
IPPROTO_EON: int
IPPROTO_ESP: int
IPPROTO_FRAGMENT: int
IPPROTO_GGP: int
IPPROTO_GRE: int
IPPROTO_HELLO: int
IPPROTO_HOPOPTS: int
IPPROTO_ICMP: int
IPPROTO_ICMPV6: int
IPPROTO_IDP: int
IPPROTO_IGMP: int
IPPROTO_IP: int
IPPROTO_IPCOMP: int
IPPROTO_IPIP: int
IPPROTO_IPV4: int
IPPROTO_IPV6: int
IPPROTO_MAX: int
IPPROTO_MOBILE: int
IPPROTO_ND: int
IPPROTO_NONE: int
IPPROTO_PIM: int
IPPROTO_PUP: int
IPPROTO_RAW: int
IPPROTO_ROUTING: int
IPPROTO_RSVP: int
```
