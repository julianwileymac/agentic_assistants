# Chunk: cb60dbd0ffd3_3

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/socket.pyi`
- lines: 374-489
- chunk: 4/9

```
S_CONG_MONITOR: int
    RDS_FREE_MR: int
    RDS_GET_MR: int
    RDS_GET_MR_FOR_DEST: int
    RDS_RDMA_DONTWAIT: int
    RDS_RDMA_FENCE: int
    RDS_RDMA_INVALIDATE: int
    RDS_RDMA_NOTIFY_ME: int
    RDS_RDMA_READWRITE: int
    RDS_RDMA_SILENT: int
    RDS_RDMA_USE_ONCE: int
    RDS_RECVERR: int

if sys.platform == "win32":
    SIO_RCVALL: int
    SIO_KEEPALIVE_VALS: int
    if sys.version_info >= (3, 6):
        SIO_LOOPBACK_FAST_PATH: int
    RCVALL_IPLEVEL: int
    RCVALL_MAX: int
    RCVALL_OFF: int
    RCVALL_ON: int
    RCVALL_SOCKETLEVELONLY: int

if sys.platform == "linux":
    AF_TIPC: AddressFamily
    SOL_TIPC: int
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

if sys.platform == "linux" and sys.version_info >= (3, 6):
    AF_ALG: AddressFamily
    SOL_ALG: int
    ALG_OP_DECRYPT: int
    ALG_OP_ENCRYPT: int
    ALG_OP_SIGN: int
    ALG_OP_VERIFY: int
    ALG_SET_AEAD_ASSOCLEN: int
    ALG_SET_AEAD_AUTHSIZE: int
    ALG_SET_IV: int
    ALG_SET_KEY: int
    ALG_SET_OP: int
    ALG_SET_PUBKEY: int

if sys.platform == "linux" and sys.version_info >= (3, 7):
    AF_VSOCK: AddressFamily
    IOCTL_VM_SOCKETS_GET_LOCAL_CID: int
    VMADDR_CID_ANY: int
    VMADDR_CID_HOST: int
    VMADDR_PORT_ANY: int
    SO_VM_SOCKETS_BUFFER_MAX_SIZE: int
    SO_VM_SOCKETS_BUFFER_SIZE: int
    SO_VM_SOCKETS_BUFFER_MIN_SIZE: int
    VM_SOCKETS_INVALID_VERSION: int

AF_LINK: AddressFamily  # Availability: BSD, macOS

# BDADDR_* and HCI_* listed with other bluetooth constants below

if sys.version_info >= (3, 6):
    SO_DOMAIN: int
    SO_PASSSEC: int
    SO_PEERSEC: int
    SO_PROTOCOL: int
    TCP_CONGESTION: int
    TCP_USER_TIMEOUT: int

if sys.platform == "linux" and sys.version_info >= (3, 8):
    AF_QIPCRTR: AddressFamily

# Semi-documented constants
# (Listed under "Socket families" in the docs, but not "Constants")

if sys.platform == "linux":
    # Netlink is defined by Linux
    AF_NETLINK: AddressFamily
    NETLINK_ARPD: int
    NETLINK_CRYPTO: int
    NETLINK_DNRTMSG: int
    NETLINK_FIREWALL: int
    NETLINK_IP6_FW: int
    NETLINK_NFLOG: int
    NETLINK_ROUTE6: int
    NETLINK_ROUTE: int
    NETLINK_SKIP: int
    NETLINK_TAPBASE: int
    NETLINK_TCPDIAG: int
    NETLINK_USERSOCK: int
    NETLINK_W1: int
    NETLINK_XFRM: int

if sys.platform != "win32" and sys.platform != "darwin":
    # Linux and some BSD support is explicit in the docs
    # Windows and macOS do not support in practice
```
