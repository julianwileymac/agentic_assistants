# Chunk: ad1a77a3d7bb_5

- source: `.venv-lab/Lib/site-packages/jinja2/utils.py`
- lines: 436-531
- chunk: 6/9

```
nly used as storage for templates this
    # won't do any harm.

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._mapping: t.Dict[t.Any, t.Any] = {}
        self._queue: te.Deque[t.Any] = deque()
        self._postinit()

    def _postinit(self) -> None:
        # alias all queue methods for faster lookup
        self._popleft = self._queue.popleft
        self._pop = self._queue.pop
        self._remove = self._queue.remove
        self._wlock = Lock()
        self._append = self._queue.append

    def __getstate__(self) -> t.Mapping[str, t.Any]:
        return {
            "capacity": self.capacity,
            "_mapping": self._mapping,
            "_queue": self._queue,
        }

    def __setstate__(self, d: t.Mapping[str, t.Any]) -> None:
        self.__dict__.update(d)
        self._postinit()

    def __getnewargs__(self) -> t.Tuple[t.Any, ...]:
        return (self.capacity,)

    def copy(self) -> "te.Self":
        """Return a shallow copy of the instance."""
        rv = self.__class__(self.capacity)
        rv._mapping.update(self._mapping)
        rv._queue.extend(self._queue)
        return rv

    def get(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Return an item from the cache dict or `default`"""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key: t.Any, default: t.Any = None) -> t.Any:
        """Set `default` if the key is not in the cache otherwise
        leave unchanged. Return the value of this key.
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def clear(self) -> None:
        """Clear the cache."""
        with self._wlock:
            self._mapping.clear()
            self._queue.clear()

    def __contains__(self, key: t.Any) -> bool:
        """Check if a key exists in this cache."""
        return key in self._mapping

    def __len__(self) -> int:
        """Return the current size of the cache."""
        return len(self._mapping)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self._mapping!r}>"

    def __getitem__(self, key: t.Any) -> t.Any:
        """Get an item from the cache. Moves the item up so that it has the
        highest priority then.

        Raise a `KeyError` if it does not exist.
        """
        with self._wlock:
            rv = self._mapping[key]

            if self._queue[-1] != key:
                try:
                    self._remove(key)
                except ValueError:
                    # if something removed the key from the container
                    # when we read, ignore the ValueError that we would
                    # get otherwise.
                    pass

                self._append(key)

            return rv

    def __setitem__(self, key: t.Any, value: t.Any) -> None:
```
