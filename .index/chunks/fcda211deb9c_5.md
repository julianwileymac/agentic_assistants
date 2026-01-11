# Chunk: fcda211deb9c_5

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 335-412
- chunk: 6/9

```
ents explicitly reflecting that fact.
        # If such events are sent regardless, VS behaves erratically. Thus, we have
        # to suppress them specifically for VS.
        if self.client.client_id not in ("visualstudio", "vsformac"):
            self.client.propagate_after_start(event)

    @message_handler
    def exited_event(self, event: messaging.Event):
        if event("pydevdReason", str, optional=True) == "processReplaced":
            # The parent process used some API like exec() that replaced it with another
            # process in situ. The connection will shut down immediately afterwards, but
            # we need to keep the corresponding session alive long enough to report the
            # subprocess to it.
            self.connection.process_replaced = True
        else:
            # If there is a launcher, it's handling the exit code.
            if not self.launcher:
                self.client.propagate_after_start(event)

    @message_handler
    def terminated_event(self, event):
        # Do not propagate this, since we'll report our own.
        self.channel.close()

    def detach_from_session(self):
        with _lock:
            self.is_connected = False
            self.channel.handlers = self.connection
            self.channel.name = self.channel.stream.name = str(self.connection)
            self.connection.server = None

    def disconnect(self):
        if self.connection.process_replaced:
            # Wait for the replacement server to connect to the adapter, and to report
            # itself to the client for this session if there is one.
            log.info("{0} is waiting for replacement subprocess.", self)
            session = self.session
            if not session.client or not session.client.is_connected:
                wait_for_connection(
                    session, lambda conn: conn.pid == self.pid, timeout=60
                )
            else:
                self.wait_for(
                    lambda: (
                        not session.client
                        or not session.client.is_connected
                        or any(
                            conn.pid == self.pid
                            for conn in session.client.known_subprocesses
                        )
                    ),
                    timeout=60,
                )
        with _lock:
            _connections.remove(self.connection)
            _connections_changed.set()
        super().disconnect()


def serve(host="127.0.0.1", port=0):
    global listener
    listener = sockets.serve("Server", Connection, host, port)
    sessions.report_sockets()
    return sockets.get_address(listener)


def is_serving():
    return listener is not None


def stop_serving():
    global listener
    try:
        if listener is not None:
            listener.close()
            listener = None
    except Exception:
```
