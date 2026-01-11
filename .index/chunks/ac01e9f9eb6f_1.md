# Chunk: ac01e9f9eb6f_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 64-142
- chunk: 2/9

```
============================
# StdIn
# =======================================================================================================================
class StdIn(BaseStdIn):
    """
    Object to be added to stdin (to emulate it as non-blocking while the next line arrives)
    """

    def __init__(self, interpreter, host, client_port, original_stdin=sys.stdin):
        BaseStdIn.__init__(self, original_stdin)
        self.interpreter = interpreter
        self.client_port = client_port
        self.host = host

    def readline(self, *args, **kwargs):
        # Ok, callback into the client to get the new input
        try:
            server = xmlrpclib.Server("http://%s:%s" % (self.host, self.client_port))
            requested_input = server.RequestInput()
            if not requested_input:
                return "\n"  # Yes, a readline must return something (otherwise we can get an EOFError on the input() call).
            else:
                # readline should end with '\n' (not doing so makes IPython 5 remove the last *valid* character).
                requested_input += "\n"
            return requested_input
        except KeyboardInterrupt:
            raise  # Let KeyboardInterrupt go through -- #PyDev-816: Interrupting infinite loop in the Interactive Console
        except:
            return "\n"

    def close(self, *args, **kwargs):
        pass  # expected in StdIn


# =======================================================================================================================
# DebugConsoleStdIn
# =======================================================================================================================
class DebugConsoleStdIn(BaseStdIn):
    """
    Object to be added to stdin (to emulate it as non-blocking while the next line arrives)
    """

    def __init__(self, py_db, original_stdin):
        """
        :param py_db:
            If None, get_global_debugger() is used.
        """
        BaseStdIn.__init__(self, original_stdin)
        self._py_db = py_db
        self._in_notification = 0

    def __send_input_requested_message(self, is_started):
        try:
            py_db = self._py_db
            if py_db is None:
                py_db = get_global_debugger()

            if py_db is None:
                return

            cmd = py_db.cmd_factory.make_input_requested_message(is_started)
            py_db.writer.add_command(cmd)
        except Exception:
            pydev_log.exception()

    @contextmanager
    def notify_input_requested(self):
        self._in_notification += 1
        if self._in_notification == 1:
            self.__send_input_requested_message(True)
        try:
            yield
        finally:
            self._in_notification -= 1
            if self._in_notification == 0:
                self.__send_input_requested_message(False)

    def readline(self, *args, **kwargs):
```
