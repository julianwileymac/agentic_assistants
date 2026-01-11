# Chunk: fdcaa9edca19_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/shortcuts/progress_bar/base.py`
- lines: 1-113
- chunk: 1/6

```
"""
Progress bar implementation on top of prompt_toolkit.

::

    with ProgressBar(...) as pb:
        for item in pb(data):
            ...
"""

from __future__ import annotations

import contextvars
import datetime
import functools
import os
import signal
import threading
import traceback
from typing import (
    Callable,
    Generic,
    Iterable,
    Iterator,
    Sequence,
    Sized,
    TextIO,
    TypeVar,
    cast,
)

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app_session
from prompt_toolkit.filters import Condition, is_done, renderer_height_is_known
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)
from prompt_toolkit.input import Input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import (
    ConditionalContainer,
    FormattedTextControl,
    HSplit,
    Layout,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import UIContent, UIControl
from prompt_toolkit.layout.dimension import AnyDimension, D
from prompt_toolkit.output import ColorDepth, Output
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.utils import in_main_thread

from .formatters import Formatter, create_default_formatters

__all__ = ["ProgressBar"]

E = KeyPressEvent

_SIGWINCH = getattr(signal, "SIGWINCH", None)


def create_key_bindings(cancel_callback: Callable[[], None] | None) -> KeyBindings:
    """
    Key bindings handled by the progress bar.
    (The main thread is not supposed to handle any key bindings.)
    """
    kb = KeyBindings()

    @kb.add("c-l")
    def _clear(event: E) -> None:
        event.app.renderer.clear()

    if cancel_callback is not None:

        @kb.add("c-c")
        def _interrupt(event: E) -> None:
            "Kill the 'body' of the progress bar, but only if we run from the main thread."
            assert cancel_callback is not None
            cancel_callback()

    return kb


_T = TypeVar("_T")


class ProgressBar:
    """
    Progress bar context manager.

    Usage ::

        with ProgressBar(...) as pb:
            for item in pb(data):
                ...

    :param title: Text to be displayed above the progress bars. This can be a
        callable or formatted text as well.
    :param formatters: List of :class:`.Formatter` instances.
    :param bottom_toolbar: Text to be displayed in the bottom toolbar. This
        can be a callable or formatted text.
    :param style: :class:`prompt_toolkit.styles.BaseStyle` instance.
    :param key_bindings: :class:`.KeyBindings` instance.
    :param cancel_callback: Callback function that's called when control-c is
        pressed by the user. This can be used for instance to start "proper"
        cancellation if the wrapped code supports it.
    :param file: The file object used for rendering, by default `sys.stderr` is used.
```
