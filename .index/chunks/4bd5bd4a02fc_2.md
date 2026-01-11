# Chunk: 4bd5bd4a02fc_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/history.py`
- lines: 168-270
- chunk: 3/4

```
r()
                    return new_items, done

                new_items, done = await loop.run_in_executor(None, in_executor)

                items_yielded += len(new_items)

                for item in new_items:
                    yield item

                if done:
                    break
        finally:
            self._string_load_events.remove(event)

    def _in_load_thread(self) -> None:
        try:
            # Start with an empty list. In case `append_string()` was called
            # before `load()` happened. Then `.store_string()` will have
            # written these entries back to disk and we will reload it.
            self._loaded_strings = []

            for item in self.history.load_history_strings():
                with self._lock:
                    self._loaded_strings.append(item)

                for event in self._string_load_events:
                    event.set()
        finally:
            with self._lock:
                self._loaded = True
            for event in self._string_load_events:
                event.set()

    def append_string(self, string: str) -> None:
        with self._lock:
            self._loaded_strings.insert(0, string)
        self.store_string(string)

    # All of the following are proxied to `self.history`.

    def load_history_strings(self) -> Iterable[str]:
        return self.history.load_history_strings()

    def store_string(self, string: str) -> None:
        self.history.store_string(string)

    def __repr__(self) -> str:
        return f"ThreadedHistory({self.history!r})"


class InMemoryHistory(History):
    """
    :class:`.History` class that keeps a list of all strings in memory.

    In order to prepopulate the history, it's possible to call either
    `append_string` for all items or pass a list of strings to `__init__` here.
    """

    def __init__(self, history_strings: Sequence[str] | None = None) -> None:
        super().__init__()
        # Emulating disk storage.
        if history_strings is None:
            self._storage = []
        else:
            self._storage = list(history_strings)

    def load_history_strings(self) -> Iterable[str]:
        yield from self._storage[::-1]

    def store_string(self, string: str) -> None:
        self._storage.append(string)


class DummyHistory(History):
    """
    :class:`.History` object that doesn't remember anything.
    """

    def load_history_strings(self) -> Iterable[str]:
        return []

    def store_string(self, string: str) -> None:
        pass

    def append_string(self, string: str) -> None:
        # Don't remember this.
        pass


_StrOrBytesPath = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]


class FileHistory(History):
    """
    :class:`.History` class that stores all strings in a file.
    """

    def __init__(self, filename: _StrOrBytesPath) -> None:
        self.filename = filename
        super().__init__()
```
