# Chunk: 6bfbecc32bf4_5

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 434-521
- chunk: 6/9

```
epth.DEPTH_24_BIT: _EscapeCodeCache(ColorDepth.DEPTH_24_BIT),
        }

        # Keep track of whether the cursor shape was ever changed.
        # (We don't restore the cursor shape if it was never changed - by
        # default, we don't change them.)
        self._cursor_shape_changed = False

        # Don't hide/show the cursor when this was already done.
        # (`None` means that we don't know whether the cursor is visible or
        # not.)
        self._cursor_visible: bool | None = None

    @classmethod
    def from_pty(
        cls,
        stdout: TextIO,
        term: str | None = None,
        default_color_depth: ColorDepth | None = None,
        enable_bell: bool = True,
    ) -> Vt100_Output:
        """
        Create an Output class from a pseudo terminal.
        (This will take the dimensions by reading the pseudo
        terminal attributes.)
        """
        fd: int | None
        # Normally, this requires a real TTY device, but people instantiate
        # this class often during unit tests as well. For convenience, we print
        # an error message, use standard dimensions, and go on.
        try:
            fd = stdout.fileno()
        except io.UnsupportedOperation:
            fd = None

        if not stdout.isatty() and (fd is None or fd not in cls._fds_not_a_terminal):
            msg = "Warning: Output is not a terminal (fd=%r).\n"
            sys.stderr.write(msg % fd)
            sys.stderr.flush()
            if fd is not None:
                cls._fds_not_a_terminal.add(fd)

        def get_size() -> Size:
            # If terminal (incorrectly) reports its size as 0, pick a
            # reasonable default.  See
            # https://github.com/ipython/ipython/issues/10071
            rows, columns = (None, None)

            # It is possible that `stdout` is no longer a TTY device at this
            # point. In that case we get an `OSError` in the ioctl call in
            # `get_size`. See:
            # https://github.com/prompt-toolkit/python-prompt-toolkit/pull/1021
            try:
                rows, columns = _get_size(stdout.fileno())
            except OSError:
                pass
            return Size(rows=rows or 24, columns=columns or 80)

        return cls(
            stdout,
            get_size,
            term=term,
            default_color_depth=default_color_depth,
            enable_bell=enable_bell,
        )

    def get_size(self) -> Size:
        return self._get_size()

    def fileno(self) -> int:
        "Return file descriptor."
        return self.stdout.fileno()

    def encoding(self) -> str:
        "Return encoding used for stdout."
        return self.stdout.encoding

    def write_raw(self, data: str) -> None:
        """
        Write raw data to output.
        """
        self._buffer.append(data)

    def write(self, data: str) -> None:
        """
        Write text to output.
        (Removes vt100 escape codes. -- used for safely writing text.)
```
