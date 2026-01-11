# Chunk: b3cdf3ca3bb0_3

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 244-335
- chunk: 4/16

```
ne line, it equals `text`."""
        return self.current_line_before_cursor + self.current_line_after_cursor

    @property
    def leading_whitespace_in_current_line(self) -> str:
        """The leading whitespace in the left margin of the current line."""
        current_line = self.current_line
        length = len(current_line) - len(current_line.lstrip())
        return current_line[:length]

    def _get_char_relative_to_cursor(self, offset: int = 0) -> str:
        """
        Return character relative to cursor position, or empty string
        """
        try:
            return self.text[self.cursor_position + offset]
        except IndexError:
            return ""

    @property
    def on_first_line(self) -> bool:
        """
        True when we are at the first line.
        """
        return self.cursor_position_row == 0

    @property
    def on_last_line(self) -> bool:
        """
        True when we are at the last line.
        """
        return self.cursor_position_row == self.line_count - 1

    @property
    def cursor_position_row(self) -> int:
        """
        Current row. (0-based.)
        """
        row, _ = self._find_line_start_index(self.cursor_position)
        return row

    @property
    def cursor_position_col(self) -> int:
        """
        Current column. (0-based.)
        """
        # (Don't use self.text_before_cursor to calculate this. Creating
        # substrings and doing rsplit is too expensive for getting the cursor
        # position.)
        _, line_start_index = self._find_line_start_index(self.cursor_position)
        return self.cursor_position - line_start_index

    def _find_line_start_index(self, index: int) -> tuple[int, int]:
        """
        For the index of a character at a certain line, calculate the index of
        the first character on that line.

        Return (row, index) tuple.
        """
        indexes = self._line_start_indexes

        pos = bisect.bisect_right(indexes, index) - 1
        return pos, indexes[pos]

    def translate_index_to_position(self, index: int) -> tuple[int, int]:
        """
        Given an index for the text, return the corresponding (row, col) tuple.
        (0-based. Returns (0, 0) for index=0.)
        """
        # Find start of this line.
        row, row_index = self._find_line_start_index(index)
        col = index - row_index

        return row, col

    def translate_row_col_to_index(self, row: int, col: int) -> int:
        """
        Given a (row, col) tuple, return the corresponding index.
        (Row and col params are 0-based.)

        Negative row/col values are turned into zero.
        """
        try:
            result = self._line_start_indexes[row]
            line = self.lines[row]
        except IndexError:
            if row < 0:
                result = self._line_start_indexes[0]
                line = self.lines[0]
            else:
                result = self._line_start_indexes[-1]
```
