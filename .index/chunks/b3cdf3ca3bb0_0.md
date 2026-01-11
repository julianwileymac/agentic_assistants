# Chunk: b3cdf3ca3bb0_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 1-98
- chunk: 1/16

```
"""
The `Document` that implements all the text operations/querying.
"""

from __future__ import annotations

import bisect
import re
import string
import weakref
from typing import Callable, Dict, Iterable, List, NoReturn, Pattern, cast

from .clipboard import ClipboardData
from .filters import vi_mode
from .selection import PasteMode, SelectionState, SelectionType

__all__ = [
    "Document",
]


# Regex for finding "words" in documents. (We consider a group of alnum
# characters a word, but also a group of special characters a word, as long as
# it doesn't contain a space.)
# (This is a 'word' in Vi.)
_FIND_WORD_RE = re.compile(r"([a-zA-Z0-9_]+|[^a-zA-Z0-9_\s]+)")
_FIND_CURRENT_WORD_RE = re.compile(r"^([a-zA-Z0-9_]+|[^a-zA-Z0-9_\s]+)")
_FIND_CURRENT_WORD_INCLUDE_TRAILING_WHITESPACE_RE = re.compile(
    r"^(([a-zA-Z0-9_]+|[^a-zA-Z0-9_\s]+)\s*)"
)

# Regex for finding "WORDS" in documents.
# (This is a 'WORD in Vi.)
_FIND_BIG_WORD_RE = re.compile(r"([^\s]+)")
_FIND_CURRENT_BIG_WORD_RE = re.compile(r"^([^\s]+)")
_FIND_CURRENT_BIG_WORD_INCLUDE_TRAILING_WHITESPACE_RE = re.compile(r"^([^\s]+\s*)")

# Share the Document._cache between all Document instances.
# (Document instances are considered immutable. That means that if another
# `Document` is constructed with the same text, it should have the same
# `_DocumentCache`.)
_text_to_document_cache: dict[str, _DocumentCache] = cast(
    Dict[str, "_DocumentCache"],
    weakref.WeakValueDictionary(),  # Maps document.text to DocumentCache instance.
)


class _ImmutableLineList(List[str]):
    """
    Some protection for our 'lines' list, which is assumed to be immutable in the cache.
    (Useful for detecting obvious bugs.)
    """

    def _error(self, *a: object, **kw: object) -> NoReturn:
        raise NotImplementedError("Attempt to modify an immutable list.")

    __setitem__ = _error
    append = _error
    clear = _error
    extend = _error
    insert = _error
    pop = _error
    remove = _error
    reverse = _error
    sort = _error


class _DocumentCache:
    def __init__(self) -> None:
        #: List of lines for the Document text.
        self.lines: _ImmutableLineList | None = None

        #: List of index positions, pointing to the start of all the lines.
        self.line_indexes: list[int] | None = None


class Document:
    """
    This is a immutable class around the text and cursor position, and contains
    methods for querying this data, e.g. to give the text before the cursor.

    This class is usually instantiated by a :class:`~prompt_toolkit.buffer.Buffer`
    object, and accessed as the `document` property of that class.

    :param text: string
    :param cursor_position: int
    :param selection: :class:`.SelectionState`
    """

    __slots__ = ("_text", "_cursor_position", "_selection", "_cache")

    def __init__(
        self,
        text: str = "",
        cursor_position: int | None = None,
        selection: SelectionState | None = None,
    ) -> None:
```
