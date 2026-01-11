# Chunk: 4fbdb5d9a49c_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/completion/base.py`
- lines: 1-88
- chunk: 1/6

```
""" """

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import AsyncGenerator, Callable, Iterable, Sequence

from prompt_toolkit.document import Document
from prompt_toolkit.eventloop import aclosing, generator_to_async_generator
from prompt_toolkit.filters import FilterOrBool, to_filter
from prompt_toolkit.formatted_text import AnyFormattedText, StyleAndTextTuples

__all__ = [
    "Completion",
    "Completer",
    "ThreadedCompleter",
    "DummyCompleter",
    "DynamicCompleter",
    "CompleteEvent",
    "ConditionalCompleter",
    "merge_completers",
    "get_common_complete_suffix",
]


class Completion:
    """
    :param text: The new string that will be inserted into the document.
    :param start_position: Position relative to the cursor_position where the
        new text will start. The text will be inserted between the
        start_position and the original cursor position.
    :param display: (optional string or formatted text) If the completion has
        to be displayed differently in the completion menu.
    :param display_meta: (Optional string or formatted text) Meta information
        about the completion, e.g. the path or source where it's coming from.
        This can also be a callable that returns a string.
    :param style: Style string.
    :param selected_style: Style string, used for a selected completion.
        This can override the `style` parameter.
    """

    def __init__(
        self,
        text: str,
        start_position: int = 0,
        display: AnyFormattedText | None = None,
        display_meta: AnyFormattedText | None = None,
        style: str = "",
        selected_style: str = "",
    ) -> None:
        from prompt_toolkit.formatted_text import to_formatted_text

        self.text = text
        self.start_position = start_position
        self._display_meta = display_meta

        if display is None:
            display = text

        self.display = to_formatted_text(display)

        self.style = style
        self.selected_style = selected_style

        assert self.start_position <= 0

    def __repr__(self) -> str:
        if isinstance(self.display, str) and self.display == self.text:
            return f"{self.__class__.__name__}(text={self.text!r}, start_position={self.start_position!r})"
        else:
            return f"{self.__class__.__name__}(text={self.text!r}, start_position={self.start_position!r}, display={self.display!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Completion):
            return False
        return (
            self.text == other.text
            and self.start_position == other.start_position
            and self.display == other.display
            and self._display_meta == other._display_meta
        )

    def __hash__(self) -> int:
        return hash((self.text, self.start_position, self.display, self._display_meta))

    @property
    def display_text(self) -> str:
```
