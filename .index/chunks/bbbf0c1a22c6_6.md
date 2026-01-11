# Chunk: bbbf0c1a22c6_6

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 486-558
- chunk: 7/9

```
    self.poller.register(self.socket, flag)
                events = self.poller.poll(0)
            else:
                events = []
        if count:  # only bypass loop if we actually flushed something
            # skip send/recv callbacks this iteration
            self._flushed = True
            # reregister them at the end of the loop
            if not already_flushed:  # don't need to do it again
                self.io_loop.add_callback(self._finish_flush)
        elif already_flushed:
            self._flushed = True

        # update ioloop poll state, which may have changed
        self._rebuild_io_state()
        return count

    def set_close_callback(self, callback: Callable | None):
        """Call the given callback when the stream is closed."""
        self._close_callback = callback

    def close(self, linger: int | None = None) -> None:
        """Close this stream."""
        if self.socket is not None:
            if self.socket.closed:
                # fallback on raw fd for closed sockets
                # hopefully this happened promptly after close,
                # otherwise somebody else may have the FD
                warnings.warn(
                    f"Unregistering FD {self._fd} after closing socket. "
                    "This could result in unregistering handlers for the wrong socket. "
                    "Please use stream.close() instead of closing the socket directly.",
                    stacklevel=2,
                )
                self.io_loop.remove_handler(self._fd)
            else:
                self.io_loop.remove_handler(self.socket)
                self.socket.close(linger)
            self.socket = None  # type: ignore
            if self._close_callback:
                self._run_callback(self._close_callback)

    def receiving(self) -> bool:
        """Returns True if we are currently receiving from the stream."""
        return self._recv_callback is not None

    def sending(self) -> bool:
        """Returns True if we are currently sending to the stream."""
        return not self._send_queue.empty()

    def closed(self) -> bool:
        if self.socket is None:
            return True
        if self.socket.closed:
            # underlying socket has been closed, but not by us!
            # trigger our cleanup
            self.close()
            return True
        return False

    def _run_callback(self, callback, *args, **kwargs):
        """Wrap running callbacks in try/except to allow us to
        close our socket."""
        try:
            f = callback(*args, **kwargs)
            if isinstance(f, Awaitable):
                f = asyncio.ensure_future(f)
            else:
                f = None
        except Exception:
            gen_log.error("Uncaught exception in ZMQStream callback", exc_info=True)
            # Re-raise the exception so that IOLoop.handle_callback_exception
```
