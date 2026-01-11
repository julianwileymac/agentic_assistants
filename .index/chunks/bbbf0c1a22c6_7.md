# Chunk: bbbf0c1a22c6_7

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 551-632
- chunk: 8/9

```
(f, Awaitable):
                f = asyncio.ensure_future(f)
            else:
                f = None
        except Exception:
            gen_log.error("Uncaught exception in ZMQStream callback", exc_info=True)
            # Re-raise the exception so that IOLoop.handle_callback_exception
            # can see it and log the error
            raise

        if f is not None:
            # handle async callbacks
            def _log_error(f):
                try:
                    f.result()
                except Exception:
                    gen_log.error(
                        "Uncaught exception in ZMQStream callback", exc_info=True
                    )

            f.add_done_callback(_log_error)

    def _handle_events(self, fd, events):
        """This method is the actual handler for IOLoop, that gets called whenever
        an event on my socket is posted. It dispatches to _handle_recv, etc."""
        if not self.socket:
            gen_log.warning("Got events for closed stream %s", self)
            return
        try:
            zmq_events = self.socket.EVENTS
        except zmq.ContextTerminated:
            gen_log.warning("Got events for stream %s after terminating context", self)
            # trigger close check, this will unregister callbacks
            self.closed()
            return
        except zmq.ZMQError as e:
            # run close check
            # shadow sockets may have been closed elsewhere,
            # which should show up as ENOTSOCK here
            if self.closed():
                gen_log.warning(
                    "Got events for stream %s attached to closed socket: %s", self, e
                )
            else:
                gen_log.error("Error getting events for %s: %s", self, e)
            return
        try:
            # dispatch events:
            if zmq_events & zmq.POLLIN and self.receiving():
                self._handle_recv()
                if not self.socket:
                    return
            if zmq_events & zmq.POLLOUT and self.sending():
                self._handle_send()
                if not self.socket:
                    return

            # rebuild the poll state
            self._rebuild_io_state()
        except Exception:
            gen_log.error("Uncaught exception in zmqstream callback", exc_info=True)
            raise

    def _handle_recv(self):
        """Handle a recv event."""
        if self._flushed:
            return
        try:
            msg = self.socket.recv_multipart(zmq.NOBLOCK, copy=self._recv_copy)
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                # state changed since poll event
                pass
            else:
                raise
        else:
            if self._recv_callback:
                callback = self._recv_callback
                self._run_callback(callback, msg)

    def _handle_send(self):
```
