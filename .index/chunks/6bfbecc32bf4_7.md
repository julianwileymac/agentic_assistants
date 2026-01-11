# Chunk: 6bfbecc32bf4_7

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 601-696
- chunk: 8/9

```
ap(self) -> None:
        self.write_raw("\x1b[?7l")

    def enable_autowrap(self) -> None:
        self.write_raw("\x1b[?7h")

    def enable_bracketed_paste(self) -> None:
        self.write_raw("\x1b[?2004h")

    def disable_bracketed_paste(self) -> None:
        self.write_raw("\x1b[?2004l")

    def reset_cursor_key_mode(self) -> None:
        """
        For vt100 only.
        Put the terminal in cursor mode (instead of application mode).
        """
        # Put the terminal in cursor mode. (Instead of application mode.)
        self.write_raw("\x1b[?1l")

    def cursor_goto(self, row: int = 0, column: int = 0) -> None:
        """
        Move cursor position.
        """
        self.write_raw("\x1b[%i;%iH" % (row, column))

    def cursor_up(self, amount: int) -> None:
        if amount == 0:
            pass
        elif amount == 1:
            self.write_raw("\x1b[A")
        else:
            self.write_raw("\x1b[%iA" % amount)

    def cursor_down(self, amount: int) -> None:
        if amount == 0:
            pass
        elif amount == 1:
            # Note: Not the same as '\n', '\n' can cause the window content to
            #       scroll.
            self.write_raw("\x1b[B")
        else:
            self.write_raw("\x1b[%iB" % amount)

    def cursor_forward(self, amount: int) -> None:
        if amount == 0:
            pass
        elif amount == 1:
            self.write_raw("\x1b[C")
        else:
            self.write_raw("\x1b[%iC" % amount)

    def cursor_backward(self, amount: int) -> None:
        if amount == 0:
            pass
        elif amount == 1:
            self.write_raw("\b")  # '\x1b[D'
        else:
            self.write_raw("\x1b[%iD" % amount)

    def hide_cursor(self) -> None:
        if self._cursor_visible in (True, None):
            self._cursor_visible = False
            self.write_raw("\x1b[?25l")

    def show_cursor(self) -> None:
        if self._cursor_visible in (False, None):
            self._cursor_visible = True
            self.write_raw("\x1b[?12l\x1b[?25h")  # Stop blinking cursor and show.

    def set_cursor_shape(self, cursor_shape: CursorShape) -> None:
        if cursor_shape == CursorShape._NEVER_CHANGE:
            return

        self._cursor_shape_changed = True
        self.write_raw(
            {
                CursorShape.BLOCK: "\x1b[2 q",
                CursorShape.BEAM: "\x1b[6 q",
                CursorShape.UNDERLINE: "\x1b[4 q",
                CursorShape.BLINKING_BLOCK: "\x1b[1 q",
                CursorShape.BLINKING_BEAM: "\x1b[5 q",
                CursorShape.BLINKING_UNDERLINE: "\x1b[3 q",
            }.get(cursor_shape, "")
        )

    def reset_cursor_shape(self) -> None:
        "Reset cursor shape."
        # (Only reset cursor shape, if we ever changed it.)
        if self._cursor_shape_changed:
            self._cursor_shape_changed = False

            # Reset cursor shape.
            self.write_raw("\x1b[0 q")
```
