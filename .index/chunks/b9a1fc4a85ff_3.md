# Chunk: b9a1fc4a85ff_3

- source: `.venv-lab/Lib/site-packages/jupyter_client/channels.py`
- lines: 245-332
- chunk: 4/4

```
   return msgs

    def msg_ready(self) -> bool:
        """Is there a message that has been received?"""
        assert self.socket is not None
        return bool(self.socket.poll(timeout=0))

    def close(self) -> None:
        """Close the socket channel."""
        if self.socket is not None:
            try:
                self.socket.close(linger=0)
            except Exception:
                pass
            self.socket = None

    stop = close

    def is_alive(self) -> bool:
        """Test whether the channel is alive."""
        return self.socket is not None

    def send(self, msg: t.Dict[str, t.Any]) -> None:
        """Pass a message to the ZMQ socket to send"""
        assert self.socket is not None
        self.session.send(self.socket, msg)

    def start(self) -> None:
        """Start the socket channel."""
        pass


class AsyncZMQSocketChannel(ZMQSocketChannel):
    """A ZMQ socket in an async API"""

    socket: zmq.asyncio.Socket

    def __init__(self, socket: zmq.asyncio.Socket, session: Session, loop: t.Any = None) -> None:
        """Create a channel.

        Parameters
        ----------
        socket : :class:`zmq.asyncio.Socket`
            The ZMQ socket to use.
        session : :class:`session.Session`
            The session to use.
        loop
            Unused here, for other implementations
        """
        if not isinstance(socket, zmq.asyncio.Socket):
            msg = "Socket must be asyncio"  # type:ignore[unreachable]
            raise ValueError(msg)
        super().__init__(socket, session)

    async def _recv(self, **kwargs: t.Any) -> t.Dict[str, t.Any]:  # type:ignore[override]
        assert self.socket is not None
        msg = await self.socket.recv_multipart(**kwargs)
        _, smsg = self.session.feed_identities(msg)
        return self.session.deserialize(smsg)

    async def get_msg(  # type:ignore[override]
        self, timeout: float | None = None
    ) -> t.Dict[str, t.Any]:
        """Gets a message if there is one that is ready."""
        assert self.socket is not None
        timeout_ms = None if timeout is None else int(timeout * 1000)  # seconds to ms
        ready = await self.socket.poll(timeout_ms)
        if ready:
            res = await self._recv()
            return res
        else:
            raise Empty

    async def get_msgs(self) -> t.List[t.Dict[str, t.Any]]:  # type:ignore[override]
        """Get all messages that are currently ready."""
        msgs = []
        while True:
            try:
                msgs.append(await self.get_msg())
            except Empty:
                break
        return msgs

    async def msg_ready(self) -> bool:  # type:ignore[override]
        """Is there a message that has been received?"""
        assert self.socket is not None
        return bool(await self.socket.poll(timeout=0))
```
