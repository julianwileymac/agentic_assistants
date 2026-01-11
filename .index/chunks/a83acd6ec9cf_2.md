# Chunk: a83acd6ec9cf_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/input/vt100_parser.py`
- lines: 174-249
- chunk: 3/4

```
| Keys | tuple[Keys, ...], insert_text: str
    ) -> None:
        """
        Callback to handler.
        """
        if isinstance(key, tuple):
            # Received ANSI sequence that corresponds with multiple keys
            # (probably alt+something). Handle keys individually, but only pass
            # data payload to first KeyPress (so that we won't insert it
            # multiple times).
            for i, k in enumerate(key):
                self._call_handler(k, insert_text if i == 0 else "")
        else:
            if key == Keys.BracketedPaste:
                self._in_bracketed_paste = True
                self._paste_buffer = ""
            else:
                self.feed_key_callback(KeyPress(key, insert_text))

    def feed(self, data: str) -> None:
        """
        Feed the input stream.

        :param data: Input string (unicode).
        """
        # Handle bracketed paste. (We bypass the parser that matches all other
        # key presses and keep reading input until we see the end mark.)
        # This is much faster then parsing character by character.
        if self._in_bracketed_paste:
            self._paste_buffer += data
            end_mark = "\x1b[201~"

            if end_mark in self._paste_buffer:
                end_index = self._paste_buffer.index(end_mark)

                # Feed content to key bindings.
                paste_content = self._paste_buffer[:end_index]
                self.feed_key_callback(KeyPress(Keys.BracketedPaste, paste_content))

                # Quit bracketed paste mode and handle remaining input.
                self._in_bracketed_paste = False
                remaining = self._paste_buffer[end_index + len(end_mark) :]
                self._paste_buffer = ""

                self.feed(remaining)

        # Handle normal input character by character.
        else:
            for i, c in enumerate(data):
                if self._in_bracketed_paste:
                    # Quit loop and process from this position when the parser
                    # entered bracketed paste.
                    self.feed(data[i:])
                    break
                else:
                    self._input_parser.send(c)

    def flush(self) -> None:
        """
        Flush the buffer of the input stream.

        This will allow us to handle the escape key (or maybe meta) sooner.
        The input received by the escape key is actually the same as the first
        characters of e.g. Arrow-Up, so without knowing what follows the escape
        sequence, we don't know whether escape has been pressed, or whether
        it's something else. This flush function should be called after a
        timeout, and processes everything that's still in the buffer as-is, so
        without assuming any characters will follow.
        """
        self._input_parser.send(_Flush())

    def feed_and_flush(self, data: str) -> None:
        """
        Wrapper around ``feed`` and ``flush``.
        """
```
