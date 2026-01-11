# Chunk: bbbf0c1a22c6_2

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 161-264
- chunk: 3/9

```
lable[[list[bytes]], Any],
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
        copy: Literal[False],
    ) -> None: ...

    @overload
    def on_recv(
        self,
        callback: Callable[[list[zmq.Frame]], Any] | Callable[[list[bytes]], Any],
        copy: bool = ...,
    ): ...

    def on_recv(
        self,
        callback: Callable[[list[zmq.Frame]], Any] | Callable[[list[bytes]], Any],
        copy: bool = True,
    ) -> None:
        """Register a callback for when a message is ready to recv.

        There can be only one callback registered at a time, so each
        call to `on_recv` replaces previously registered callbacks.

        on_recv(None) disables recv event polling.

        Use on_recv_stream(callback) instead, to register a callback that will receive
        both this ZMQStream and the message, instead of just the message.

        Parameters
        ----------

        callback : callable
            callback must take exactly one argument, which will be a
            list, as returned by socket.recv_multipart()
            if callback is None, recv callbacks are disabled.
        copy : bool
            copy is passed directly to recv, so if copy is False,
            callback will receive Message objects. If copy is True,
            then callback will receive bytes/str objects.

        Returns : None
        """

        self._check_closed()
        assert callback is None or callable(callback)
        self._recv_callback = callback
        self._recv_copy = copy
        if callback is None:
            self._drop_io_state(zmq.POLLIN)
        else:
            self._add_io_state(zmq.POLLIN)

    @overload
    def on_recv_stream(
        self,
        callback: Callable[[ZMQStream, list[bytes]], Any],
    ) -> None: ...

    @overload
    def on_recv_stream(
        self,
        callback: Callable[[ZMQStream, list[bytes]], Any],
        copy: Literal[True],
    ) -> None: ...

    @overload
    def on_recv_stream(
        self,
        callback: Callable[[ZMQStream, list[zmq.Frame]], Any],
        copy: Literal[False],
    ) -> None: ...

    @overload
    def on_recv_stream(
        self,
        callback: (
            Callable[[ZMQStream, list[zmq.Frame]], Any]
            | Callable[[ZMQStream, list[bytes]], Any]
        ),
        copy: bool = ...,
    ): ...

    def on_recv_stream(
        self,
        callback: (
            Callable[[ZMQStream, list[zmq.Frame]], Any]
            | Callable[[ZMQStream, list[bytes]], Any]
        ),
        copy: bool = True,
    ):
        """Same as on_recv, but callback will get this stream as first argument

```
