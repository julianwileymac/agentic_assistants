# Chunk: bbbf0c1a22c6_4

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 335-425
- chunk: 5/9

```
se:
            self.on_send(lambda msg, status: callback(self, msg, status))

    def send(self, msg, flags=0, copy=True, track=False, callback=None, **kwargs):
        """Send a message, optionally also register a new callback for sends.
        See zmq.socket.send for details.
        """
        return self.send_multipart(
            [msg], flags=flags, copy=copy, track=track, callback=callback, **kwargs
        )

    def send_multipart(
        self,
        msg: Sequence[Any],
        flags: int = 0,
        copy: bool = True,
        track: bool = False,
        callback: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a multipart message, optionally also register a new callback for sends.
        See zmq.socket.send_multipart for details.
        """
        kwargs.update(dict(flags=flags, copy=copy, track=track))
        self._send_queue.put((msg, kwargs))
        callback = callback or self._send_callback
        if callback is not None:
            self.on_send(callback)
        else:
            # noop callback
            self.on_send(lambda *args: None)
        self._add_io_state(zmq.POLLOUT)

    def send_string(
        self,
        u: str,
        flags: int = 0,
        encoding: str = 'utf-8',
        callback: Callable | None = None,
        **kwargs: Any,
    ):
        """Send a unicode message with an encoding.
        See zmq.socket.send_unicode for details.
        """
        if not isinstance(u, str):
            raise TypeError("unicode/str objects only")
        return self.send(u.encode(encoding), flags=flags, callback=callback, **kwargs)

    send_unicode = send_string

    def send_json(
        self,
        obj: Any,
        flags: int = 0,
        callback: Callable | None = None,
        **kwargs: Any,
    ):
        """Send json-serialized version of an object.
        See zmq.socket.send_json for details.
        """
        msg = jsonapi.dumps(obj)
        return self.send(msg, flags=flags, callback=callback, **kwargs)

    def send_pyobj(
        self,
        obj: Any,
        flags: int = 0,
        protocol: int = -1,
        callback: Callable | None = None,
        **kwargs: Any,
    ):
        """Send a Python object as a message using pickle to serialize.

        See zmq.socket.send_json for details.
        """
        msg = pickle.dumps(obj, protocol)
        return self.send(msg, flags, callback=callback, **kwargs)

    def _finish_flush(self):
        """callback for unsetting _flushed flag."""
        self._flushed = False

    def flush(self, flag: int = zmq.POLLIN | zmq.POLLOUT, limit: int | None = None):
        """Flush pending messages.

        This method safely handles all pending incoming and/or outgoing messages,
        bypassing the inner loop, passing them to the registered callbacks.

        A limit can be specified, to prevent blocking under high load.

```
