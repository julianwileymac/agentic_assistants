# Chunk: b3cdf3ca3bb0_4

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 326-417
- chunk: 5/16

```

            result = self._line_start_indexes[row]
            line = self.lines[row]
        except IndexError:
            if row < 0:
                result = self._line_start_indexes[0]
                line = self.lines[0]
            else:
                result = self._line_start_indexes[-1]
                line = self.lines[-1]

        result += max(0, min(col, len(line)))

        # Keep in range. (len(self.text) is included, because the cursor can be
        # right after the end of the text as well.)
        result = max(0, min(result, len(self.text)))
        return result

    @property
    def is_cursor_at_the_end(self) -> bool:
        """True when the cursor is at the end of the text."""
        return self.cursor_position == len(self.text)

    @property
    def is_cursor_at_the_end_of_line(self) -> bool:
        """True when the cursor is at the end of this line."""
        return self.current_char in ("\n", "")

    def has_match_at_current_position(self, sub: str) -> bool:
        """
        `True` when this substring is found at the cursor position.
        """
        return self.text.find(sub, self.cursor_position) == self.cursor_position

    def find(
        self,
        sub: str,
        in_current_line: bool = False,
        include_current_position: bool = False,
        ignore_case: bool = False,
        count: int = 1,
    ) -> int | None:
        """
        Find `text` after the cursor, return position relative to the cursor
        position. Return `None` if nothing was found.

        :param count: Find the n-th occurrence.
        """
        assert isinstance(ignore_case, bool)

        if in_current_line:
            text = self.current_line_after_cursor
        else:
            text = self.text_after_cursor

        if not include_current_position:
            if len(text) == 0:
                return None  # (Otherwise, we always get a match for the empty string.)
            else:
                text = text[1:]

        flags = re.IGNORECASE if ignore_case else 0
        iterator = re.finditer(re.escape(sub), text, flags)

        try:
            for i, match in enumerate(iterator):
                if i + 1 == count:
                    if include_current_position:
                        return match.start(0)
                    else:
                        return match.start(0) + 1
        except StopIteration:
            pass
        return None

    def find_all(self, sub: str, ignore_case: bool = False) -> list[int]:
        """
        Find all occurrences of the substring. Return a list of absolute
        positions in the document.
        """
        flags = re.IGNORECASE if ignore_case else 0
        return [a.start() for a in re.finditer(re.escape(sub), self.text, flags)]

    def find_backwards(
        self,
        sub: str,
        in_current_line: bool = False,
        ignore_case: bool = False,
        count: int = 1,
    ) -> int | None:
        """
```
