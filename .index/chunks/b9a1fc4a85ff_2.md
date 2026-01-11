# Chunk: b9a1fc4a85ff_2

- source: `.venv-lab/Lib/site-packages/jupyter_client/channels.py`
- lines: 161-255
- chunk: 3/4

```
       self._pause = False

    def is_beating(self) -> bool:
        """Is the heartbeat running and responsive (and not paused)."""
        if self.is_alive() and not self._pause and self._beating:  # noqa
            return True
        else:
            return False

    def stop(self) -> None:
        """Stop the channel's event loop and join its thread."""
        self._running = False
        self._exit.set()
        self.join()
        self.close()

    def close(self) -> None:
        """Close the heartbeat thread."""
        if self.socket is not None:
            try:
                self.socket.close(linger=0)
            except Exception:
                pass
            self.socket = None

    def call_handlers(self, since_last_heartbeat: float) -> None:
        """This method is called in the ioloop thread when a message arrives.

        Subclasses should override this method to handle incoming messages.
        It is important to remember that this method is called in the thread
        so that some logic must be done to ensure that the application level
        handlers are called in the application thread.
        """
        pass


HBChannelABC.register(HBChannel)


class ZMQSocketChannel:
    """A ZMQ socket wrapper"""

    def __init__(self, socket: zmq.Socket, session: Session, loop: t.Any = None) -> None:
        """Create a channel.

        Parameters
        ----------
        socket : :class:`zmq.Socket`
            The ZMQ socket to use.
        session : :class:`session.Session`
            The session to use.
        loop
            Unused here, for other implementations
        """
        super().__init__()

        self.socket: zmq.Socket | None = socket
        self.session = session

    def _recv(self, **kwargs: t.Any) -> t.Dict[str, t.Any]:
        assert self.socket is not None
        msg = self.socket.recv_multipart(**kwargs)
        _ident, smsg = self.session.feed_identities(msg)
        return self.session.deserialize(smsg)

    def get_msg(self, timeout: float | None = None) -> t.Dict[str, t.Any]:
        """Gets a message if there is one that is ready."""
        assert self.socket is not None
        timeout_ms = None if timeout is None else int(timeout * 1000)  # seconds to ms
        ready = self.socket.poll(timeout_ms)
        if ready:
            res = self._recv()
            return res
        else:
            raise Empty

    def get_msgs(self) -> t.List[t.Dict[str, t.Any]]:
        """Get all messages that are currently ready."""
        msgs = []
        while True:
            try:
                msgs.append(self.get_msg())
            except Empty:
                break
        return msgs

    def msg_ready(self) -> bool:
        """Is there a message that has been received?"""
        assert self.socket is not None
        return bool(self.socket.poll(timeout=0))

    def close(self) -> None:
        """Close the socket channel."""
        if self.socket is not None:
```
