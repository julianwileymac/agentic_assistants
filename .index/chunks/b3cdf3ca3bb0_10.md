# Chunk: b3cdf3ca3bb0_10

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 807-896
- chunk: 11/16

```
rt_pos - 1, -1):
            c = self.text[i]

            if c == right_ch:
                stack += 1
            elif c == left_ch:
                stack -= 1

            if stack == 0:
                return i - self.cursor_position

        return None

    def find_matching_bracket_position(
        self, start_pos: int | None = None, end_pos: int | None = None
    ) -> int:
        """
        Return relative cursor position of matching [, (, { or < bracket.

        When `start_pos` or `end_pos` are given. Don't look past the positions.
        """

        # Look for a match.
        for pair in "()", "[]", "{}", "<>":
            A = pair[0]
            B = pair[1]
            if self.current_char == A:
                return self.find_enclosing_bracket_right(A, B, end_pos=end_pos) or 0
            elif self.current_char == B:
                return self.find_enclosing_bracket_left(A, B, start_pos=start_pos) or 0

        return 0

    def get_start_of_document_position(self) -> int:
        """Relative position for the start of the document."""
        return -self.cursor_position

    def get_end_of_document_position(self) -> int:
        """Relative position for the end of the document."""
        return len(self.text) - self.cursor_position

    def get_start_of_line_position(self, after_whitespace: bool = False) -> int:
        """Relative position for the start of this line."""
        if after_whitespace:
            current_line = self.current_line
            return (
                len(current_line)
                - len(current_line.lstrip())
                - self.cursor_position_col
            )
        else:
            return -len(self.current_line_before_cursor)

    def get_end_of_line_position(self) -> int:
        """Relative position for the end of this line."""
        return len(self.current_line_after_cursor)

    def last_non_blank_of_current_line_position(self) -> int:
        """
        Relative position for the last non blank character of this line.
        """
        return len(self.current_line.rstrip()) - self.cursor_position_col - 1

    def get_column_cursor_position(self, column: int) -> int:
        """
        Return the relative cursor position for this column at the current
        line. (It will stay between the boundaries of the line in case of a
        larger number.)
        """
        line_length = len(self.current_line)
        current_column = self.cursor_position_col
        column = max(0, min(line_length, column))

        return column - current_column

    def selection_range(
        self,
    ) -> tuple[
        int, int
    ]:  # XXX: shouldn't this return `None` if there is no selection???
        """
        Return (from, to) tuple of the selection.
        start and end position are included.

        This doesn't take the selection type into account. Use
        `selection_ranges` instead.
        """
        if self.selection:
            from_, to = sorted(
```
