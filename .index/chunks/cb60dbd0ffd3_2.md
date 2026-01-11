# Chunk: cb60dbd0ffd3_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/socket.pyi`
- lines: 262-387
- chunk: 3/9

```
: int
TCP_QUICKACK: int
TCP_SYNCNT: int
TCP_WINDOW_CLAMP: int
if sys.version_info >= (3, 7):
    TCP_NOTSENT_LOWAT: int

# Specifically-documented constants

if sys.platform == "linux" and sys.version_info >= (3,):
    AF_CAN: AddressFamily
    PF_CAN: int
    SOL_CAN_BASE: int
    SOL_CAN_RAW: int
    CAN_EFF_FLAG: int
    CAN_EFF_MASK: int
    CAN_ERR_FLAG: int
    CAN_ERR_MASK: int
    CAN_RAW: int
    CAN_RAW_ERR_FILTER: int
    CAN_RAW_FILTER: int
    CAN_RAW_LOOPBACK: int
    CAN_RAW_RECV_OWN_MSGS: int
    CAN_RTR_FLAG: int
    CAN_SFF_MASK: int

    CAN_BCM: int
    CAN_BCM_TX_SETUP: int
    CAN_BCM_TX_DELETE: int
    CAN_BCM_TX_READ: int
    CAN_BCM_TX_SEND: int
    CAN_BCM_RX_SETUP: int
    CAN_BCM_RX_DELETE: int
    CAN_BCM_RX_READ: int
    CAN_BCM_TX_STATUS: int
    CAN_BCM_TX_EXPIRED: int
    CAN_BCM_RX_STATUS: int
    CAN_BCM_RX_TIMEOUT: int
    CAN_BCM_RX_CHANGED: int

    CAN_RAW_FD_FRAMES: int

if sys.platform == "linux" and sys.version_info >= (3, 8):
    CAN_BCM_SETTIMER: int
    CAN_BCM_STARTTIMER: int
    CAN_BCM_TX_COUNTEVT: int
    CAN_BCM_TX_ANNOUNCE: int
    CAN_BCM_TX_CP_CAN_ID: int
    CAN_BCM_RX_FILTER_ID: int
    CAN_BCM_RX_CHECK_DLC: int
    CAN_BCM_RX_NO_AUTOTIMER: int
    CAN_BCM_RX_ANNOUNCE_RESUME: int
    CAN_BCM_TX_RESET_MULTI_IDX: int
    CAN_BCM_RX_RTR_FRAME: int
    CAN_BCM_CAN_FD_FRAME: int

if sys.platform == "linux" and sys.version_info >= (3, 7):
    CAN_ISOTP: int

if sys.platform == "linux" and sys.version_info >= (3, 9):
    CAN_J1939: int

    J1939_MAX_UNICAST_ADDR: int
    J1939_IDLE_ADDR: int
    J1939_NO_ADDR: int
    J1939_NO_NAME: int
    J1939_PGN_REQUEST: int
    J1939_PGN_ADDRESS_CLAIMED: int
    J1939_PGN_ADDRESS_COMMANDED: int
    J1939_PGN_PDU1_MAX: int
    J1939_PGN_MAX: int
    J1939_NO_PGN: int

    SO_J1939_FILTER: int
    SO_J1939_PROMISC: int
    SO_J1939_SEND_PRIO: int
    SO_J1939_ERRQUEUE: int

    SCM_J1939_DEST_ADDR: int
    SCM_J1939_DEST_NAME: int
    SCM_J1939_PRIO: int
    SCM_J1939_ERRQUEUE: int

    J1939_NLA_PAD: int
    J1939_NLA_BYTES_ACKED: int

    J1939_EE_INFO_NONE: int
    J1939_EE_INFO_TX_ABORT: int

    J1939_FILTER_MAX: int

if sys.platform == "linux":
    AF_PACKET: AddressFamily
    PF_PACKET: int
    PACKET_BROADCAST: int
    PACKET_FASTROUTE: int
    PACKET_HOST: int
    PACKET_LOOPBACK: int
    PACKET_MULTICAST: int
    PACKET_OTHERHOST: int
    PACKET_OUTGOING: int

if sys.platform == "linux" and sys.version_info >= (3,):
    AF_RDS: AddressFamily
    PF_RDS: int
    SOL_RDS: int
    RDS_CANCEL_SENT_TO: int
    RDS_CMSG_RDMA_ARGS: int
    RDS_CMSG_RDMA_DEST: int
    RDS_CMSG_RDMA_MAP: int
    RDS_CMSG_RDMA_STATUS: int
    RDS_CMSG_RDMA_UPDATE: int
    RDS_CONG_MONITOR: int
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
```
