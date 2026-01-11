# Chunk: fcda211deb9c_2

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 147-223
- chunk: 3/9

```
first server, this is expected, since
        # it corresponds to the root process, and there is no other debug session to
        # notify. But subsequent server connections represent subprocesses, and those
        # will not start running user code until the client tells them to. Since there
        # isn't going to be a client without the notification, such subprocesses have
        # to be unblocked.
        if is_first_server:
            return
        log.info("No clients to wait for - unblocking {0}.", self)
        try:
            self.channel.request("initialize", {"adapterID": "debugpy"})
            self.channel.request("attach", {"subProcessId": self.pid})
            self.channel.request("configurationDone")
            self.channel.request("disconnect")
        except Exception:
            log.swallow_exception("Failed to unblock orphaned subprocess:")
            self.channel.close()

    def __str__(self):
        return "Server" + ("[?]" if self.pid is None else f"[pid={self.pid}]")

    def authenticate(self):
        if access_token is None and adapter.access_token is None:
            return
        auth = self.channel.request(
            "pydevdAuthorize", {"debugServerAccessToken": access_token}
        )
        if auth["clientAccessToken"] != adapter.access_token:
            self.channel.close()
            raise RuntimeError('Mismatched "clientAccessToken"; server not authorized.')

    def request(self, request):
        raise request.isnt_valid(
            "Requests from the debug server to the client are not allowed."
        )

    def event(self, event):
        pass

    def terminated_event(self, event):
        self.channel.close()

    def disconnect(self):
        with _lock:
            self.disconnected = True
            if self.server is not None:
                # If the disconnect happened while Server was being instantiated,
                # we need to tell it, so that it can clean up via Session.finalize().
                # It will also take care of deregistering the connection in that case.
                self.server.disconnect()
            elif self in _connections:
                _connections.remove(self)
                _connections_changed.set()

    def attach_to_session(self, session):
        """Attaches this server to the specified Session as a Server component.

        Raises ValueError if the server already belongs to some session.
        """

        with _lock:
            if self.server is not None:
                raise ValueError
            log.info("Attaching {0} to {1}", self, session)
            self.server = Server(session, self)


class Server(components.Component):
    """Handles the debug server side of a debug session."""

    message_handler = components.Component.message_handler

    connection: Connection

    class Capabilities(components.Capabilities):
        PROPERTIES = {
```
