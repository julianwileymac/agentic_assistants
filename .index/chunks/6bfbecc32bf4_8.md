# Chunk: 6bfbecc32bf4_8

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 685-761
- chunk: 9/9

```
    )

    def reset_cursor_shape(self) -> None:
        "Reset cursor shape."
        # (Only reset cursor shape, if we ever changed it.)
        if self._cursor_shape_changed:
            self._cursor_shape_changed = False

            # Reset cursor shape.
            self.write_raw("\x1b[0 q")

    def flush(self) -> None:
        """
        Write to output stream and flush.
        """
        if not self._buffer:
            return

        data = "".join(self._buffer)
        self._buffer = []

        flush_stdout(self.stdout, data)

    def ask_for_cpr(self) -> None:
        """
        Asks for a cursor position report (CPR).
        """
        self.write_raw("\x1b[6n")
        self.flush()

    @property
    def responds_to_cpr(self) -> bool:
        if not self.enable_cpr:
            return False

        # When the input is a tty, we assume that CPR is supported.
        # It's not when the input is piped from Pexpect.
        if os.environ.get("PROMPT_TOOLKIT_NO_CPR", "") == "1":
            return False

        if is_dumb_terminal(self.term):
            return False
        try:
            return self.stdout.isatty()
        except ValueError:
            return False  # ValueError: I/O operation on closed file

    def bell(self) -> None:
        "Sound bell."
        if self.enable_bell:
            self.write_raw("\a")
            self.flush()

    def get_default_color_depth(self) -> ColorDepth:
        """
        Return the default color depth for a vt100 terminal, according to the
        our term value.

        We prefer 256 colors almost always, because this is what most terminals
        support these days, and is a good default.
        """
        if self.default_color_depth is not None:
            return self.default_color_depth

        term = self.term

        if term is None:
            return ColorDepth.DEFAULT

        if is_dumb_terminal(term):
            return ColorDepth.DEPTH_1_BIT

        if term in ("linux", "eterm-color"):
            return ColorDepth.DEPTH_4_BIT

        return ColorDepth.DEFAULT
```
