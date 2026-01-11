# Chunk: 6bfbecc32bf4_6

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 509-613
- chunk: 7/9

```
encoding

    def write_raw(self, data: str) -> None:
        """
        Write raw data to output.
        """
        self._buffer.append(data)

    def write(self, data: str) -> None:
        """
        Write text to output.
        (Removes vt100 escape codes. -- used for safely writing text.)
        """
        self._buffer.append(data.replace("\x1b", "?"))

    def set_title(self, title: str) -> None:
        """
        Set terminal title.
        """
        if self.term not in (
            "linux",
            "eterm-color",
        ):  # Not supported by the Linux console.
            self.write_raw(
                "\x1b]2;{}\x07".format(title.replace("\x1b", "").replace("\x07", ""))
            )

    def clear_title(self) -> None:
        self.set_title("")

    def erase_screen(self) -> None:
        """
        Erases the screen with the background color and moves the cursor to
        home.
        """
        self.write_raw("\x1b[2J")

    def enter_alternate_screen(self) -> None:
        self.write_raw("\x1b[?1049h\x1b[H")

    def quit_alternate_screen(self) -> None:
        self.write_raw("\x1b[?1049l")

    def enable_mouse_support(self) -> None:
        self.write_raw("\x1b[?1000h")

        # Enable mouse-drag support.
        self.write_raw("\x1b[?1003h")

        # Enable urxvt Mouse mode. (For terminals that understand this.)
        self.write_raw("\x1b[?1015h")

        # Also enable Xterm SGR mouse mode. (For terminals that understand this.)
        self.write_raw("\x1b[?1006h")

        # Note: E.g. lxterminal understands 1000h, but not the urxvt or sgr
        #       extensions.

    def disable_mouse_support(self) -> None:
        self.write_raw("\x1b[?1000l")
        self.write_raw("\x1b[?1015l")
        self.write_raw("\x1b[?1006l")
        self.write_raw("\x1b[?1003l")

    def erase_end_of_line(self) -> None:
        """
        Erases from the current cursor position to the end of the current line.
        """
        self.write_raw("\x1b[K")

    def erase_down(self) -> None:
        """
        Erases the screen from the current line down to the bottom of the
        screen.
        """
        self.write_raw("\x1b[J")

    def reset_attributes(self) -> None:
        self.write_raw("\x1b[0m")

    def set_attributes(self, attrs: Attrs, color_depth: ColorDepth) -> None:
        """
        Create new style and output.

        :param attrs: `Attrs` instance.
        """
        # Get current depth.
        escape_code_cache = self._escape_code_caches[color_depth]

        # Write escape character.
        self.write_raw(escape_code_cache[attrs])

    def disable_autowrap(self) -> None:
        self.write_raw("\x1b[?7l")

    def enable_autowrap(self) -> None:
        self.write_raw("\x1b[?7h")

    def enable_bracketed_paste(self) -> None:
        self.write_raw("\x1b[?2004h")

    def disable_bracketed_paste(self) -> None:
        self.write_raw("\x1b[?2004l")
```
