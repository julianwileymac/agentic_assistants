# Chunk: cc4c3c8aea41_1

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 96-183
- chunk: 2/14

```
eger(
        0,
        config=True,
        help="""Timeout (in seconds) after which a kernel is considered idle and ready to be culled.
        Values of 0 or lower disable culling. Very short timeouts may result in kernels being culled
        for users with poor network connections.""",
    )

    cull_interval_default = 300  # 5 minutes
    cull_interval = Integer(
        cull_interval_default,
        config=True,
        help="""The interval (in seconds) on which to check for idle kernels exceeding the cull timeout value.""",
    )

    cull_connected = Bool(
        False,
        config=True,
        help="""Whether to consider culling kernels which have one or more connections.
        Only effective if cull_idle_timeout > 0.""",
    )

    cull_busy = Bool(
        False,
        config=True,
        help="""Whether to consider culling kernels which are busy.
        Only effective if cull_idle_timeout > 0.""",
    )

    buffer_offline_messages = Bool(
        True,
        config=True,
        help="""Whether messages from kernels whose frontends have disconnected should be buffered in-memory.

        When True (default), messages are buffered and replayed on reconnect,
        avoiding lost messages due to interrupted connectivity.

        Disable if long-running kernels will produce too much output while
        no frontends are connected.
        """,
    )

    kernel_info_timeout = Float(
        60,
        config=True,
        help="""Timeout for giving up on a kernel (in seconds).

        On starting and restarting kernels, we check whether the
        kernel is running and responsive by sending kernel_info_requests.
        This sets the timeout in seconds for how long the kernel can take
        before being presumed dead.
        This affects the MappingKernelManager (which handles kernel restarts)
        and the ZMQChannelsHandler (which handles the startup).
        """,
    )

    _kernel_buffers = Any()

    @default("_kernel_buffers")
    def _default_kernel_buffers(self):
        return defaultdict(lambda: {"buffer": [], "session_key": "", "channels": {}})

    last_kernel_activity = Instance(
        datetime,
        help="The last activity on any kernel, including shutting down a kernel",
    )

    def __init__(self, **kwargs):
        """Initialize a kernel manager."""
        self.pinned_superclass = MultiKernelManager
        self._pending_kernel_tasks = {}
        self.pinned_superclass.__init__(self, **kwargs)
        self.last_kernel_activity = utcnow()

    allowed_message_types = List(
        trait=Unicode(),
        config=True,
        help="""White list of allowed kernel message types.
        When the list is empty, all message types are allowed.
        """,
    )

    allow_tracebacks = Bool(
        True, config=True, help=("Whether to send tracebacks to clients on exceptions.")
    )

    traceback_replacement_message = Unicode(
```
