# Chunk: b3cdf3ca3bb0_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 161-251
- chunk: 3/16

```
"
        return self._get_char_relative_to_cursor(0) or ""

    @property
    def char_before_cursor(self) -> str:
        """Return character before the cursor or an empty string."""
        return self._get_char_relative_to_cursor(-1) or ""

    @property
    def text_before_cursor(self) -> str:
        return self.text[: self.cursor_position :]

    @property
    def text_after_cursor(self) -> str:
        return self.text[self.cursor_position :]

    @property
    def current_line_before_cursor(self) -> str:
        """Text from the start of the line until the cursor."""
        _, _, text = self.text_before_cursor.rpartition("\n")
        return text

    @property
    def current_line_after_cursor(self) -> str:
        """Text from the cursor until the end of the line."""
        text, _, _ = self.text_after_cursor.partition("\n")
        return text

    @property
    def lines(self) -> list[str]:
        """
        Array of all the lines.
        """
        # Cache, because this one is reused very often.
        if self._cache.lines is None:
            self._cache.lines = _ImmutableLineList(self.text.split("\n"))

        return self._cache.lines

    @property
    def _line_start_indexes(self) -> list[int]:
        """
        Array pointing to the start indexes of all the lines.
        """
        # Cache, because this is often reused. (If it is used, it's often used
        # many times. And this has to be fast for editing big documents!)
        if self._cache.line_indexes is None:
            # Create list of line lengths.
            line_lengths = map(len, self.lines)

            # Calculate cumulative sums.
            indexes = [0]
            append = indexes.append
            pos = 0

            for line_length in line_lengths:
                pos += line_length + 1
                append(pos)

            # Remove the last item. (This is not a new line.)
            if len(indexes) > 1:
                indexes.pop()

            self._cache.line_indexes = indexes

        return self._cache.line_indexes

    @property
    def lines_from_current(self) -> list[str]:
        """
        Array of the lines starting from the current line, until the last line.
        """
        return self.lines[self.cursor_position_row :]

    @property
    def line_count(self) -> int:
        r"""Return the number of lines in this document. If the document ends
        with a trailing \n, that counts as the beginning of a new line."""
        return len(self.lines)

    @property
    def current_line(self) -> str:
        """Return the text on the line where the cursor is. (when the input
        consists of just one line, it equals `text`."""
        return self.current_line_before_cursor + self.current_line_after_cursor

    @property
    def leading_whitespace_in_current_line(self) -> str:
        """The leading whitespace in the left margin of the current line."""
        current_line = self.current_line
```
