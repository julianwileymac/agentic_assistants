# Chunk: fcda211deb9c_6

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 397-501
- chunk: 7/9

```
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
        log.swallow_exception(level="warning")
    sessions.report_sockets()


def connections():
    with _lock:
        return list(_connections)


def wait_for_connection(session, predicate, timeout=None):
    """Waits until there is a server matching the specified predicate connected to
    this adapter, and returns the corresponding Connection.

    If there is more than one server connection already available, returns the oldest
    one.
    """

    def wait_for_timeout():
        time.sleep(timeout)
        wait_for_timeout.timed_out = True
        with _lock:
            _connections_changed.set()

    wait_for_timeout.timed_out = timeout == 0
    if timeout:
        thread = threading.Thread(
            target=wait_for_timeout, name="servers.wait_for_connection() timeout"
        )
        thread.daemon = True
        thread.start()

    if timeout != 0:
        log.info("{0} waiting for connection from debug server...", session)
    while True:
        with _lock:
            _connections_changed.clear()
            conns = (conn for conn in _connections if predicate(conn))
            conn = next(conns, None)
            if conn is not None or wait_for_timeout.timed_out:
                return conn
        _connections_changed.wait()


def wait_until_disconnected():
    """Blocks until all debug servers disconnect from the adapter.

    If there are no server connections, waits until at least one is established first,
    before waiting for it to disconnect.
    """
    while True:
        _connections_changed.wait()
        with _lock:
            _connections_changed.clear()
            if not len(_connections):
                return


def dont_wait_for_first_connection():
    """Unblocks any pending wait_until_disconnected() call that is waiting on the
    first server to connect.
    """
    with _lock:
        _connections_changed.set()


def inject(pid, debugpy_args, on_output):
    host, port = sockets.get_address(listener)

    cmdline = [
        sys.executable,
        os.path.dirname(debugpy.__file__),
        "--connect",
        host + ":" + str(port),
    ]
    if adapter.access_token is not None:
        cmdline += ["--adapter-access-token", adapter.access_token]
    cmdline += debugpy_args
    cmdline += ["--pid", str(pid)]

    log.info("Spawning attach-to-PID debugger injector: {0!r}", cmdline)
    try:
        injector = subprocess.Popen(
            cmdline,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except Exception as exc:
```
