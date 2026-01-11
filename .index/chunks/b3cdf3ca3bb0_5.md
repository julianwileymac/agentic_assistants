# Chunk: b3cdf3ca3bb0_5

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 406-494
- chunk: 6/16

```
ORECASE if ignore_case else 0
        return [a.start() for a in re.finditer(re.escape(sub), self.text, flags)]

    def find_backwards(
        self,
        sub: str,
        in_current_line: bool = False,
        ignore_case: bool = False,
        count: int = 1,
    ) -> int | None:
        """
        Find `text` before the cursor, return position relative to the cursor
        position. Return `None` if nothing was found.

        :param count: Find the n-th occurrence.
        """
        if in_current_line:
            before_cursor = self.current_line_before_cursor[::-1]
        else:
            before_cursor = self.text_before_cursor[::-1]

        flags = re.IGNORECASE if ignore_case else 0
        iterator = re.finditer(re.escape(sub[::-1]), before_cursor, flags)

        try:
            for i, match in enumerate(iterator):
                if i + 1 == count:
                    return -match.start(0) - len(sub)
        except StopIteration:
            pass
        return None

    def get_word_before_cursor(
        self, WORD: bool = False, pattern: Pattern[str] | None = None
    ) -> str:
        """
        Give the word before the cursor.
        If we have whitespace before the cursor this returns an empty string.

        :param pattern: (None or compiled regex). When given, use this regex
            pattern.
        """
        if self._is_word_before_cursor_complete(WORD=WORD, pattern=pattern):
            # Space before the cursor or no text before cursor.
            return ""

        text_before_cursor = self.text_before_cursor
        start = self.find_start_of_previous_word(WORD=WORD, pattern=pattern) or 0

        return text_before_cursor[len(text_before_cursor) + start :]

    def _is_word_before_cursor_complete(
        self, WORD: bool = False, pattern: Pattern[str] | None = None
    ) -> bool:
        if pattern:
            return self.find_start_of_previous_word(WORD=WORD, pattern=pattern) is None
        else:
            return (
                self.text_before_cursor == "" or self.text_before_cursor[-1:].isspace()
            )

    def find_start_of_previous_word(
        self, count: int = 1, WORD: bool = False, pattern: Pattern[str] | None = None
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the start
        of the previous word. Return `None` if nothing was found.

        :param pattern: (None or compiled regex). When given, use this regex
            pattern.
        """
        assert not (WORD and pattern)

        # Reverse the text before the cursor, in order to do an efficient
        # backwards search.
        text_before_cursor = self.text_before_cursor[::-1]

        if pattern:
            regex = pattern
        elif WORD:
            regex = _FIND_BIG_WORD_RE
        else:
            regex = _FIND_WORD_RE

        iterator = regex.finditer(text_before_cursor)

        try:
            for i, match in enumerate(iterator):
```
