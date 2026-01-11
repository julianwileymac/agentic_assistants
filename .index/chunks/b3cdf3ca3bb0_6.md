# Chunk: b3cdf3ca3bb0_6

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 481-558
- chunk: 7/16

```
lf.text_before_cursor[::-1]

        if pattern:
            regex = pattern
        elif WORD:
            regex = _FIND_BIG_WORD_RE
        else:
            regex = _FIND_WORD_RE

        iterator = regex.finditer(text_before_cursor)

        try:
            for i, match in enumerate(iterator):
                if i + 1 == count:
                    return -match.end(0)
        except StopIteration:
            pass
        return None

    def find_boundaries_of_current_word(
        self,
        WORD: bool = False,
        include_leading_whitespace: bool = False,
        include_trailing_whitespace: bool = False,
    ) -> tuple[int, int]:
        """
        Return the relative boundaries (startpos, endpos) of the current word under the
        cursor. (This is at the current line, because line boundaries obviously
        don't belong to any word.)
        If not on a word, this returns (0,0)
        """
        text_before_cursor = self.current_line_before_cursor[::-1]
        text_after_cursor = self.current_line_after_cursor

        def get_regex(include_whitespace: bool) -> Pattern[str]:
            return {
                (False, False): _FIND_CURRENT_WORD_RE,
                (False, True): _FIND_CURRENT_WORD_INCLUDE_TRAILING_WHITESPACE_RE,
                (True, False): _FIND_CURRENT_BIG_WORD_RE,
                (True, True): _FIND_CURRENT_BIG_WORD_INCLUDE_TRAILING_WHITESPACE_RE,
            }[(WORD, include_whitespace)]

        match_before = get_regex(include_leading_whitespace).search(text_before_cursor)
        match_after = get_regex(include_trailing_whitespace).search(text_after_cursor)

        # When there is a match before and after, and we're not looking for
        # WORDs, make sure that both the part before and after the cursor are
        # either in the [a-zA-Z_] alphabet or not. Otherwise, drop the part
        # before the cursor.
        if not WORD and match_before and match_after:
            c1 = self.text[self.cursor_position - 1]
            c2 = self.text[self.cursor_position]
            alphabet = string.ascii_letters + "0123456789_"

            if (c1 in alphabet) != (c2 in alphabet):
                match_before = None

        return (
            -match_before.end(1) if match_before else 0,
            match_after.end(1) if match_after else 0,
        )

    def get_word_under_cursor(self, WORD: bool = False) -> str:
        """
        Return the word, currently below the cursor.
        This returns an empty string when the cursor is on a whitespace region.
        """
        start, end = self.find_boundaries_of_current_word(WORD=WORD)
        return self.text[self.cursor_position + start : self.cursor_position + end]

    def find_next_word_beginning(
        self, count: int = 1, WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the start
        of the next word. Return `None` if nothing was found.
        """
```
