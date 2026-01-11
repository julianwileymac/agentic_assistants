# Chunk: bbbf0c1a22c6_1

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 88-175
- chunk: 2/9

```
nd_queue: Queue
    _recv_callback: Callable | None
    _send_callback: Callable | None
    _close_callback: Callable | None
    _state: int = 0
    _flushed: bool = False
    _recv_copy: bool = False
    _fd: int

    def __init__(self, socket: zmq.Socket, io_loop: IOLoop | None = None):
        if isinstance(socket, zmq._future._AsyncSocket):
            warnings.warn(
                f"""ZMQStream only supports the base zmq.Socket class.

                Use zmq.Socket(shadow=other_socket)
                or `ctx.socket(zmq.{socket._type_name}, socket_class=zmq.Socket)`
                to create a base zmq.Socket object,
                no matter what other kind of socket your Context creates.
                """,
                RuntimeWarning,
                stacklevel=2,
            )
            # shadow back to base zmq.Socket,
            # otherwise callbacks like `on_recv` will get the wrong types.
            socket = zmq.Socket(shadow=socket)
        self.socket = socket

        # IOLoop.current() is deprecated if called outside the event loop
        # that means
        self.io_loop = io_loop or IOLoop.current()
        self.poller = zmq.Poller()
        self._fd = cast(int, self.socket.FD)

        self._send_queue = Queue()
        self._recv_callback = None
        self._send_callback = None
        self._close_callback = None
        self._recv_copy = False
        self._flushed = False

        self._state = 0
        self._init_io_state()

        # shortcircuit some socket methods
        self.bind = self.socket.bind
        self.bind_to_random_port = self.socket.bind_to_random_port
        self.connect = self.socket.connect
        self.setsockopt = self.socket.setsockopt
        self.getsockopt = self.socket.getsockopt
        self.setsockopt_string = self.socket.setsockopt_string
        self.getsockopt_string = self.socket.getsockopt_string
        self.setsockopt_unicode = self.socket.setsockopt_unicode
        self.getsockopt_unicode = self.socket.getsockopt_unicode

    def stop_on_recv(self):
        """Disable callback and automatic receiving."""
        return self.on_recv(None)

    def stop_on_send(self):
        """Disable callback on sending."""
        return self.on_send(None)

    def stop_on_err(self):
        """DEPRECATED, does nothing"""
        gen_log.warn("on_err does nothing, and will be removed")

    def on_err(self, callback: Callable):
        """DEPRECATED, does nothing"""
        gen_log.warn("on_err does nothing, and will be removed")

    @overload
    def on_recv(
        self,
        callback: Callable[[list[bytes]], Any],
    ) -> None: ...

    @overload
    def on_recv(
        self,
        callback: Callable[[list[bytes]], Any],
        copy: Literal[True],
    ) -> None: ...

    @overload
    def on_recv(
        self,
        callback: Callable[[list[zmq.Frame]], Any],
```
