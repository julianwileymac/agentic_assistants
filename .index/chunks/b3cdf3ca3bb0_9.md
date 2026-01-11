# Chunk: b3cdf3ca3bb0_9

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 717-821
- chunk: 10/16

```
arrow-up button.

        :param preferred_column: When given, go to this column instead of
                                 staying at the current column.
        """
        assert count >= 1
        column = (
            self.cursor_position_col if preferred_column is None else preferred_column
        )

        return (
            self.translate_row_col_to_index(
                max(0, self.cursor_position_row - count), column
            )
            - self.cursor_position
        )

    def get_cursor_down_position(
        self, count: int = 1, preferred_column: int | None = None
    ) -> int:
        """
        Return the relative cursor position (character index) where we would be if the
        user pressed the arrow-down button.

        :param preferred_column: When given, go to this column instead of
                                 staying at the current column.
        """
        assert count >= 1
        column = (
            self.cursor_position_col if preferred_column is None else preferred_column
        )

        return (
            self.translate_row_col_to_index(self.cursor_position_row + count, column)
            - self.cursor_position
        )

    def find_enclosing_bracket_right(
        self, left_ch: str, right_ch: str, end_pos: int | None = None
    ) -> int | None:
        """
        Find the right bracket enclosing current position. Return the relative
        position to the cursor position.

        When `end_pos` is given, don't look past the position.
        """
        if self.current_char == right_ch:
            return 0

        if end_pos is None:
            end_pos = len(self.text)
        else:
            end_pos = min(len(self.text), end_pos)

        stack = 1

        # Look forward.
        for i in range(self.cursor_position + 1, end_pos):
            c = self.text[i]

            if c == left_ch:
                stack += 1
            elif c == right_ch:
                stack -= 1

            if stack == 0:
                return i - self.cursor_position

        return None

    def find_enclosing_bracket_left(
        self, left_ch: str, right_ch: str, start_pos: int | None = None
    ) -> int | None:
        """
        Find the left bracket enclosing current position. Return the relative
        position to the cursor position.

        When `start_pos` is given, don't look past the position.
        """
        if self.current_char == left_ch:
            return 0

        if start_pos is None:
            start_pos = 0
        else:
            start_pos = max(0, start_pos)

        stack = 1

        # Look backward.
        for i in range(self.cursor_position - 1, start_pos - 1, -1):
            c = self.text[i]

            if c == right_ch:
                stack += 1
            elif c == left_ch:
                stack -= 1

            if stack == 0:
                return i - self.cursor_position

        return None

    def find_matching_bracket_position(
```
