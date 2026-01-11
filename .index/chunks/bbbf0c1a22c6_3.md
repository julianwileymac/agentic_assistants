# Chunk: bbbf0c1a22c6_3

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 254-342
- chunk: 4/9

```
def on_recv_stream(
        self,
        callback: (
            Callable[[ZMQStream, list[zmq.Frame]], Any]
            | Callable[[ZMQStream, list[bytes]], Any]
        ),
        copy: bool = True,
    ):
        """Same as on_recv, but callback will get this stream as first argument

        callback must take exactly two arguments, as it will be called as::

            callback(stream, msg)

        Useful when a single callback should be used with multiple streams.
        """
        if callback is None:
            self.stop_on_recv()
        else:

            def stream_callback(msg):
                return callback(self, msg)

            self.on_recv(stream_callback, copy=copy)

    def on_send(
        self, callback: Callable[[Sequence[Any], zmq.MessageTracker | None], Any]
    ):
        """Register a callback to be called on each send

        There will be two arguments::

            callback(msg, status)

        * `msg` will be the list of sendable objects that was just sent
        * `status` will be the return result of socket.send_multipart(msg) -
          MessageTracker or None.

        Non-copying sends return a MessageTracker object whose
        `done` attribute will be True when the send is complete.
        This allows users to track when an object is safe to write to
        again.

        The second argument will always be None if copy=True
        on the send.

        Use on_send_stream(callback) to register a callback that will be passed
        this ZMQStream as the first argument, in addition to the other two.

        on_send(None) disables recv event polling.

        Parameters
        ----------

        callback : callable
            callback must take exactly two arguments, which will be
            the message being sent (always a list),
            and the return result of socket.send_multipart(msg) -
            MessageTracker or None.

            if callback is None, send callbacks are disabled.
        """

        self._check_closed()
        assert callback is None or callable(callback)
        self._send_callback = callback

    def on_send_stream(
        self,
        callback: Callable[[ZMQStream, Sequence[Any], zmq.MessageTracker | None], Any],
    ):
        """Same as on_send, but callback will get this stream as first argument

        Callback will be passed three arguments::

            callback(stream, msg, status)

        Useful when a single callback should be used with multiple streams.
        """
        if callback is None:
            self.stop_on_send()
        else:
            self.on_send(lambda msg, status: callback(self, msg, status))

    def send(self, msg, flags=0, copy=True, track=False, callback=None, **kwargs):
        """Send a message, optionally also register a new callback for sends.
        See zmq.socket.send for details.
        """
```
