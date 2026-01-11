# Chunk: ce92ab9adeed_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_console.py`
- lines: 69-147
- chunk: 2/4

```
ef readline(self, *args, **kwargs):
        sys.stderr.write("Warning: Reading from stdin is still not supported in this console.\n")
        return "\n"


# =======================================================================================================================
# DebugConsole
# =======================================================================================================================
class DebugConsole(InteractiveConsole, BaseInterpreterInterface):
    """Wrapper around code.InteractiveConsole, in order to send
    errors and outputs to the debug console
    """

    @overrides(BaseInterpreterInterface.create_std_in)
    def create_std_in(self, *args, **kwargs):
        try:
            if not self.__buffer_output:
                return sys.stdin
        except:
            pass

        return _DebugConsoleStdIn()  # If buffered, raw_input is not supported in this console.

    @overrides(InteractiveConsole.push)
    def push(self, line, frame, buffer_output=True):
        """Change built-in stdout and stderr methods by the
        new custom StdMessage.
        execute the InteractiveConsole.push.
        Change the stdout and stderr back be the original built-ins

        :param buffer_output: if False won't redirect the output.

        Return boolean (True if more input is required else False),
        output_messages and input_messages
        """
        self.__buffer_output = buffer_output
        more = False
        if buffer_output:
            original_stdout = sys.stdout
            original_stderr = sys.stderr
        try:
            try:
                self.frame = frame
                if buffer_output:
                    out = sys.stdout = IOBuf()
                    err = sys.stderr = IOBuf()
                more = self.add_exec(line)
            except Exception:
                exc = get_exception_traceback_str()
                if buffer_output:
                    err.buflist.append("Internal Error: %s" % (exc,))
                else:
                    sys.stderr.write("Internal Error: %s\n" % (exc,))
        finally:
            # Remove frame references.
            self.frame = None
            frame = None
            if buffer_output:
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        if buffer_output:
            return more, out.buflist, err.buflist
        else:
            return more, [], []

    @overrides(BaseInterpreterInterface.do_add_exec)
    def do_add_exec(self, line):
        return InteractiveConsole.push(self, line)

    @overrides(InteractiveConsole.runcode)
    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

```
