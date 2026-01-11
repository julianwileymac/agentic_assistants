# Chunk: fcda211deb9c_1

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 92-151
- chunk: 2/9

```
 # deregister it.
                if self.disconnected:
                    return

                # An existing connection with the same PID and process_replaced == True
                # corresponds to the process that replaced itself with this one, so it's
                # not an error.
                if any(
                    conn.pid == self.pid and not conn.process_replaced
                    for conn in _connections
                ):
                    raise KeyError(f"{self} is already connected to this adapter")

                is_first_server = len(_connections) == 0
                _connections.append(self)
                _connections_changed.set()

        except Exception:
            log.swallow_exception("Failed to accept incoming server connection:")
            self.channel.close()

            # If this was the first server to connect, and the main thread is inside
            # wait_until_disconnected(), we want to unblock it and allow it to exit.
            dont_wait_for_first_connection()

            # If we couldn't retrieve all the necessary info from the debug server,
            # or there's a PID clash, we don't want to track this debuggee anymore,
            # but we want to continue accepting connections.
            return

        parent_session = sessions.get(self.ppid)
        if parent_session is None:
            parent_session = sessions.get(self.pid)
        if parent_session is None:
            log.info("No active debug session for parent process of {0}.", self)
        else:
            if self.pid == parent_session.pid:
                parent_server = parent_session.server
                if not (parent_server and parent_server.connection.process_replaced):
                    log.error("{0} is not expecting replacement.", parent_session)
                    self.channel.close()
                    return
            try:
                parent_session.client.notify_of_subprocess(self)
                return
            except Exception:
                # This might fail if the client concurrently disconnects from the parent
                # session. We still want to keep the connection around, in case the
                # client reconnects later. If the parent session was "launch", it'll take
                # care of closing the remaining server connections.
                log.swallow_exception(
                    "Failed to notify parent session about {0}:", self
                )

        # If we got to this point, the subprocess notification was either not sent,
        # or not delivered successfully. For the first server, this is expected, since
        # it corresponds to the root process, and there is no other debug session to
        # notify. But subsequent server connections represent subprocesses, and those
        # will not start running user code until the client tells them to. Since there
```
