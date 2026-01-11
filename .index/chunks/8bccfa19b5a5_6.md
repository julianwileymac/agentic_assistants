# Chunk: 8bccfa19b5a5_6

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 508-571
- chunk: 7/7

```
ontext manager:

    >>> async def f2():
    ...    with (yield lock.acquire()):
    ...        # Do something holding the lock.
    ...        pass
    ...
    ...    # Now the lock is released.

    .. versionchanged:: 4.3
       Added ``async with`` support in Python 3.5.

    """

    def __init__(self) -> None:
        self._block = BoundedSemaphore(value=1)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} _block={self._block}>"

    def acquire(
        self, timeout: Optional[Union[float, datetime.timedelta]] = None
    ) -> Awaitable[_ReleasingContextManager]:
        """Attempt to lock. Returns an awaitable.

        Returns an awaitable, which raises `tornado.util.TimeoutError` after a
        timeout.
        """
        return self._block.acquire(timeout)

    def release(self) -> None:
        """Unlock.

        The first coroutine in line waiting for `acquire` gets the lock.

        If not locked, raise a `RuntimeError`.
        """
        try:
            self._block.release()
        except ValueError:
            raise RuntimeError("release unlocked lock")

    def __enter__(self) -> None:
        raise RuntimeError("Use `async with` instead of `with` for Lock")

    def __exit__(
        self,
        typ: "Optional[Type[BaseException]]",
        value: Optional[BaseException],
        tb: Optional[types.TracebackType],
    ) -> None:
        self.__enter__()

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(
        self,
        typ: "Optional[Type[BaseException]]",
        value: Optional[BaseException],
        tb: Optional[types.TracebackType],
    ) -> None:
        self.release()
```
