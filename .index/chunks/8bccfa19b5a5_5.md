# Chunk: 8bccfa19b5a5_5

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 425-522
- chunk: 6/7

```
tManager(self))
        else:
            self._waiters.append(waiter)
            if timeout:

                def on_timeout() -> None:
                    if not waiter.done():
                        waiter.set_exception(gen.TimeoutError())
                    self._garbage_collect()

                io_loop = ioloop.IOLoop.current()
                timeout_handle = io_loop.add_timeout(timeout, on_timeout)
                waiter.add_done_callback(
                    lambda _: io_loop.remove_timeout(timeout_handle)
                )
        return waiter

    def __enter__(self) -> None:
        raise RuntimeError("Use 'async with' instead of 'with' for Semaphore")

    def __exit__(
        self,
        typ: "Optional[Type[BaseException]]",
        value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
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


class BoundedSemaphore(Semaphore):
    """A semaphore that prevents release() being called too many times.

    If `.release` would increment the semaphore's value past the initial
    value, it raises `ValueError`. Semaphores are mostly used to guard
    resources with limited capacity, so a semaphore released too many times
    is a sign of a bug.
    """

    def __init__(self, value: int = 1) -> None:
        super().__init__(value=value)
        self._initial_value = value

    def release(self) -> None:
        """Increment the counter and wake one waiter."""
        if self._value >= self._initial_value:
            raise ValueError("Semaphore released too many times")
        super().release()


class Lock:
    """A lock for coroutines.

    A Lock begins unlocked, and `acquire` locks it immediately. While it is
    locked, a coroutine that yields `acquire` waits until another coroutine
    calls `release`.

    Releasing an unlocked lock raises `RuntimeError`.

    A Lock can be used as an async context manager with the ``async
    with`` statement:

    >>> from tornado import locks
    >>> lock = locks.Lock()
    >>>
    >>> async def f():
    ...    async with lock:
    ...        # Do something holding the lock.
    ...        pass
    ...
    ...    # Now the lock is released.

    For compatibility with older versions of Python, the `.acquire`
    method asynchronously returns a regular context manager:

    >>> async def f2():
    ...    with (yield lock.acquire()):
    ...        # Do something holding the lock.
    ...        pass
    ...
    ...    # Now the lock is released.

    .. versionchanged:: 4.3
       Added ``async with`` support in Python 3.5.

    """

```
