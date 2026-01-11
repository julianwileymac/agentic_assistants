# Chunk: b3cdf3ca3bb0_8

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 630-725
- chunk: 9/16

```
WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the end
        of the previous word. Return `None` if nothing was found.
        """
        if count < 0:
            return self.find_next_word_ending(count=-count, WORD=WORD)

        text_before_cursor = self.text_after_cursor[:1] + self.text_before_cursor[::-1]

        regex = _FIND_BIG_WORD_RE if WORD else _FIND_WORD_RE
        iterator = regex.finditer(text_before_cursor)

        try:
            for i, match in enumerate(iterator):
                # Take first match, unless it's the word on which we're right now.
                if i == 0 and match.start(1) == 0:
                    count += 1

                if i + 1 == count:
                    return -match.start(1) + 1
        except StopIteration:
            pass
        return None

    def find_next_matching_line(
        self, match_func: Callable[[str], bool], count: int = 1
    ) -> int | None:
        """
        Look downwards for empty lines.
        Return the line index, relative to the current line.
        """
        result = None

        for index, line in enumerate(self.lines[self.cursor_position_row + 1 :]):
            if match_func(line):
                result = 1 + index
                count -= 1

            if count == 0:
                break

        return result

    def find_previous_matching_line(
        self, match_func: Callable[[str], bool], count: int = 1
    ) -> int | None:
        """
        Look upwards for empty lines.
        Return the line index, relative to the current line.
        """
        result = None

        for index, line in enumerate(self.lines[: self.cursor_position_row][::-1]):
            if match_func(line):
                result = -1 - index
                count -= 1

            if count == 0:
                break

        return result

    def get_cursor_left_position(self, count: int = 1) -> int:
        """
        Relative position for cursor left.
        """
        if count < 0:
            return self.get_cursor_right_position(-count)

        return -min(self.cursor_position_col, count)

    def get_cursor_right_position(self, count: int = 1) -> int:
        """
        Relative position for cursor_right.
        """
        if count < 0:
            return self.get_cursor_left_position(-count)

        return min(count, len(self.current_line_after_cursor))

    def get_cursor_up_position(
        self, count: int = 1, preferred_column: int | None = None
    ) -> int:
        """
        Return the relative cursor position (character index) where we would be if the
        user pressed the arrow-up button.

        :param preferred_column: When given, go to this column instead of
                                 staying at the current column.
        """
        assert count >= 1
        column = (
            self.cursor_position_col if preferred_column is None else preferred_column
```
