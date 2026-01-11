# Chunk: bbbf0c1a22c6_8

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 621-689
- chunk: 9/9

```
N:
                # state changed since poll event
                pass
            else:
                raise
        else:
            if self._recv_callback:
                callback = self._recv_callback
                self._run_callback(callback, msg)

    def _handle_send(self):
        """Handle a send event."""
        if self._flushed:
            return
        if not self.sending():
            gen_log.error("Shouldn't have handled a send event")
            return

        msg, kwargs = self._send_queue.get()
        try:
            status = self.socket.send_multipart(msg, **kwargs)
        except zmq.ZMQError as e:
            gen_log.error("SEND Error: %s", e)
            status = e
        if self._send_callback:
            callback = self._send_callback
            self._run_callback(callback, msg, status)

    def _check_closed(self):
        if not self.socket:
            raise OSError("Stream is closed")

    def _rebuild_io_state(self):
        """rebuild io state based on self.sending() and receiving()"""
        if self.socket is None:
            return
        state = 0
        if self.receiving():
            state |= zmq.POLLIN
        if self.sending():
            state |= zmq.POLLOUT

        self._state = state
        self._update_handler(state)

    def _add_io_state(self, state):
        """Add io_state to poller."""
        self._state = self._state | state
        self._update_handler(self._state)

    def _drop_io_state(self, state):
        """Stop poller from watching an io_state."""
        self._state = self._state & (~state)
        self._update_handler(self._state)

    def _update_handler(self, state):
        """Update IOLoop handler with state."""
        if self.socket is None:
            return

        if state & self.socket.events:
            # events still exist that haven't been processed
            # explicitly schedule handling to avoid missing events due to edge-triggered FDs
            self.io_loop.add_callback(lambda: self._handle_events(self.socket, 0))

    def _init_io_state(self):
        """initialize the ioloop event handler"""
        self.io_loop.add_handler(self.socket, self._handle_events, self.io_loop.READ)
```
