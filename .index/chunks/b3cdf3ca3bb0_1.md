# Chunk: b3cdf3ca3bb0_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 86-171
- chunk: 2/16

```
ion: int
    :param selection: :class:`.SelectionState`
    """

    __slots__ = ("_text", "_cursor_position", "_selection", "_cache")

    def __init__(
        self,
        text: str = "",
        cursor_position: int | None = None,
        selection: SelectionState | None = None,
    ) -> None:
        # Check cursor position. It can also be right after the end. (Where we
        # insert text.)
        assert cursor_position is None or cursor_position <= len(text), AssertionError(
            f"cursor_position={cursor_position!r}, len_text={len(text)!r}"
        )

        # By default, if no cursor position was given, make sure to put the
        # cursor position is at the end of the document. This is what makes
        # sense in most places.
        if cursor_position is None:
            cursor_position = len(text)

        # Keep these attributes private. A `Document` really has to be
        # considered to be immutable, because otherwise the caching will break
        # things. Because of that, we wrap these into read-only properties.
        self._text = text
        self._cursor_position = cursor_position
        self._selection = selection

        # Cache for lines/indexes. (Shared with other Document instances that
        # contain the same text.
        try:
            self._cache = _text_to_document_cache[self.text]
        except KeyError:
            self._cache = _DocumentCache()
            _text_to_document_cache[self.text] = self._cache

        # XX: For some reason, above, we can't use 'WeakValueDictionary.setdefault'.
        #     This fails in Pypy3. `self._cache` becomes None, because that's what
        #     'setdefault' returns.
        # self._cache = _text_to_document_cache.setdefault(self.text, _DocumentCache())
        # assert self._cache

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.text!r}, {self.cursor_position!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Document):
            return False

        return (
            self.text == other.text
            and self.cursor_position == other.cursor_position
            and self.selection == other.selection
        )

    @property
    def text(self) -> str:
        "The document text."
        return self._text

    @property
    def cursor_position(self) -> int:
        "The document cursor position."
        return self._cursor_position

    @property
    def selection(self) -> SelectionState | None:
        ":class:`.SelectionState` object."
        return self._selection

    @property
    def current_char(self) -> str:
        """Return character under cursor or an empty string."""
        return self._get_char_relative_to_cursor(0) or ""

    @property
    def char_before_cursor(self) -> str:
        """Return character before the cursor or an empty string."""
        return self._get_char_relative_to_cursor(-1) or ""

    @property
    def text_before_cursor(self) -> str:
```
