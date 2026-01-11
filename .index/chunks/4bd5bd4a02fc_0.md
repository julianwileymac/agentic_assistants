# Chunk: 4bd5bd4a02fc_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/history.py`
- lines: 1-106
- chunk: 1/4

```
"""
Implementations for the history of a `Buffer`.

NOTE: There is no `DynamicHistory`:
      This doesn't work well, because the `Buffer` needs to be able to attach
      an event handler to the event when a history entry is loaded. This
      loading can be done asynchronously and making the history swappable would
      probably break this.
"""

from __future__ import annotations

import datetime
import os
import threading
from abc import ABCMeta, abstractmethod
from asyncio import get_running_loop
from typing import AsyncGenerator, Iterable, Sequence, Union

__all__ = [
    "History",
    "ThreadedHistory",
    "DummyHistory",
    "FileHistory",
    "InMemoryHistory",
]


class History(metaclass=ABCMeta):
    """
    Base ``History`` class.

    This also includes abstract methods for loading/storing history.
    """

    def __init__(self) -> None:
        # In memory storage for strings.
        self._loaded = False

        # History that's loaded already, in reverse order. Latest, most recent
        # item first.
        self._loaded_strings: list[str] = []

    #
    # Methods expected by `Buffer`.
    #

    async def load(self) -> AsyncGenerator[str, None]:
        """
        Load the history and yield all the entries in reverse order (latest,
        most recent history entry first).

        This method can be called multiple times from the `Buffer` to
        repopulate the history when prompting for a new input. So we are
        responsible here for both caching, and making sure that strings that
        were were appended to the history will be incorporated next time this
        method is called.
        """
        if not self._loaded:
            self._loaded_strings = list(self.load_history_strings())
            self._loaded = True

        for item in self._loaded_strings:
            yield item

    def get_strings(self) -> list[str]:
        """
        Get the strings from the history that are loaded so far.
        (In order. Oldest item first.)
        """
        return self._loaded_strings[::-1]

    def append_string(self, string: str) -> None:
        "Add string to the history."
        self._loaded_strings.insert(0, string)
        self.store_string(string)

    #
    # Implementation for specific backends.
    #

    @abstractmethod
    def load_history_strings(self) -> Iterable[str]:
        """
        This should be a generator that yields `str` instances.

        It should yield the most recent items first, because they are the most
        important. (The history can already be used, even when it's only
        partially loaded.)
        """
        while False:
            yield

    @abstractmethod
    def store_string(self, string: str) -> None:
        """
        Store the string in persistent storage.
        """


class ThreadedHistory(History):
    """
    Wrapper around `History` implementations that run the `load()` generator in
    a thread.
```
