# Chunk: b3cdf3ca3bb0_7

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 549-639
- chunk: 8/16

```
 : self.cursor_position + end]

    def find_next_word_beginning(
        self, count: int = 1, WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the start
        of the next word. Return `None` if nothing was found.
        """
        if count < 0:
            return self.find_previous_word_beginning(count=-count, WORD=WORD)

        regex = _FIND_BIG_WORD_RE if WORD else _FIND_WORD_RE
        iterator = regex.finditer(self.text_after_cursor)

        try:
            for i, match in enumerate(iterator):
                # Take first match, unless it's the word on which we're right now.
                if i == 0 and match.start(1) == 0:
                    count += 1

                if i + 1 == count:
                    return match.start(1)
        except StopIteration:
            pass
        return None

    def find_next_word_ending(
        self, include_current_position: bool = False, count: int = 1, WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the end
        of the next word. Return `None` if nothing was found.
        """
        if count < 0:
            return self.find_previous_word_ending(count=-count, WORD=WORD)

        if include_current_position:
            text = self.text_after_cursor
        else:
            text = self.text_after_cursor[1:]

        regex = _FIND_BIG_WORD_RE if WORD else _FIND_WORD_RE
        iterable = regex.finditer(text)

        try:
            for i, match in enumerate(iterable):
                if i + 1 == count:
                    value = match.end(1)

                    if include_current_position:
                        return value
                    else:
                        return value + 1

        except StopIteration:
            pass
        return None

    def find_previous_word_beginning(
        self, count: int = 1, WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the start
        of the previous word. Return `None` if nothing was found.
        """
        if count < 0:
            return self.find_next_word_beginning(count=-count, WORD=WORD)

        regex = _FIND_BIG_WORD_RE if WORD else _FIND_WORD_RE
        iterator = regex.finditer(self.text_before_cursor[::-1])

        try:
            for i, match in enumerate(iterator):
                if i + 1 == count:
                    return -match.end(1)
        except StopIteration:
            pass
        return None

    def find_previous_word_ending(
        self, count: int = 1, WORD: bool = False
    ) -> int | None:
        """
        Return an index relative to the cursor position pointing to the end
        of the previous word. Return `None` if nothing was found.
        """
        if count < 0:
            return self.find_next_word_ending(count=-count, WORD=WORD)
```
