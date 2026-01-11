# Chunk: ac01e9f9eb6f_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 203-274
- chunk: 4/9

```
       #
            #     for i in range(10): print(i)
            #
            # (in a single line) don't work.
            # Note that it won't give an error and code will be None (so, it'll
            # use execMultipleLines in the next call in this case).
            symbol = "single"
            code = self.interpreter.compile(source, "<input>", symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            return False
        if code is None:
            # Case 2
            return True

        # Case 3
        return False

    def need_more(self, code_fragment):
        if self.buffer is None:
            self.buffer = code_fragment
        else:
            self.buffer.append(code_fragment)

        return self.need_more_for_code(self.buffer.text)

    def create_std_in(self, debugger=None, original_std_in=None):
        if debugger is None:
            return StdIn(self, self.host, self.client_port, original_stdin=original_std_in)
        else:
            return DebugConsoleStdIn(py_db=debugger, original_stdin=original_std_in)

    def add_exec(self, code_fragment, debugger=None):
        # In case sys.excepthook called, use original excepthook #PyDev-877: Debug console freezes with Python 3.5+
        # (showtraceback does it on python 3.5 onwards)
        sys.excepthook = sys.__excepthook__
        try:
            original_in = sys.stdin
            try:
                help = None
                if "pydoc" in sys.modules:
                    pydoc = sys.modules["pydoc"]  # Don't import it if it still is not there.

                    if hasattr(pydoc, "help"):
                        # You never know how will the API be changed, so, let's code defensively here
                        help = pydoc.help
                        if not hasattr(help, "input"):
                            help = None
            except:
                # Just ignore any error here
                pass

            more = False
            try:
                sys.stdin = self.create_std_in(debugger, original_in)
                try:
                    if help is not None:
                        # This will enable the help() function to work.
                        try:
                            try:
                                help.input = sys.stdin
                            except AttributeError:
                                help._input = sys.stdin
                        except:
                            help = None
                            if not self._input_error_printed:
                                self._input_error_printed = True
                                sys.stderr.write("\nError when trying to update pydoc.help.input\n")
                                sys.stderr.write("(help() may not work -- please report this as a bug in the pydev bugtracker).\n\n")
                                traceback.print_exc()

```
