# Chunk: a3be15a24edc_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/base.py`
- lines: 1-117
- chunk: 1/3

```
"""
Interface for an output.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TextIO

from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.data_structures import Size
from prompt_toolkit.styles import Attrs

from .color_depth import ColorDepth

__all__ = [
    "Output",
    "DummyOutput",
]


class Output(metaclass=ABCMeta):
    """
    Base class defining the output interface for a
    :class:`~prompt_toolkit.renderer.Renderer`.

    Actual implementations are
    :class:`~prompt_toolkit.output.vt100.Vt100_Output` and
    :class:`~prompt_toolkit.output.win32.Win32Output`.
    """

    stdout: TextIO | None = None

    @abstractmethod
    def fileno(self) -> int:
        "Return the file descriptor to which we can write for the output."

    @abstractmethod
    def encoding(self) -> str:
        """
        Return the encoding for this output, e.g. 'utf-8'.
        (This is used mainly to know which characters are supported by the
        output the data, so that the UI can provide alternatives, when
        required.)
        """

    @abstractmethod
    def write(self, data: str) -> None:
        "Write text (Terminal escape sequences will be removed/escaped.)"

    @abstractmethod
    def write_raw(self, data: str) -> None:
        "Write text."

    @abstractmethod
    def set_title(self, title: str) -> None:
        "Set terminal title."

    @abstractmethod
    def clear_title(self) -> None:
        "Clear title again. (or restore previous title.)"

    @abstractmethod
    def flush(self) -> None:
        "Write to output stream and flush."

    @abstractmethod
    def erase_screen(self) -> None:
        """
        Erases the screen with the background color and moves the cursor to
        home.
        """

    @abstractmethod
    def enter_alternate_screen(self) -> None:
        "Go to the alternate screen buffer. (For full screen applications)."

    @abstractmethod
    def quit_alternate_screen(self) -> None:
        "Leave the alternate screen buffer."

    @abstractmethod
    def enable_mouse_support(self) -> None:
        "Enable mouse."

    @abstractmethod
    def disable_mouse_support(self) -> None:
        "Disable mouse."

    @abstractmethod
    def erase_end_of_line(self) -> None:
        """
        Erases from the current cursor position to the end of the current line.
        """

    @abstractmethod
    def erase_down(self) -> None:
        """
        Erases the screen from the current line down to the bottom of the
        screen.
        """

    @abstractmethod
    def reset_attributes(self) -> None:
        "Reset color and styling attributes."

    @abstractmethod
    def set_attributes(self, attrs: Attrs, color_depth: ColorDepth) -> None:
        "Set new color and styling attributes."

    @abstractmethod
    def disable_autowrap(self) -> None:
        "Disable auto line wrapping."

    @abstractmethod
    def enable_autowrap(self) -> None:
```
