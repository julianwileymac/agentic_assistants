# Chunk: 8bccfa19b5a5_2

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 164-271
- chunk: 3/7

```
ed:

    .. testcode::

        import asyncio
        from tornado import gen
        from tornado.locks import Event

        event = Event()

        async def waiter():
            print("Waiting for event")
            await event.wait()
            print("Not waiting this time")
            await event.wait()
            print("Done")

        async def setter():
            print("About to set the event")
            event.set()

        async def runner():
            await gen.multi([waiter(), setter()])

        asyncio.run(runner())

    .. testoutput::

        Waiting for event
        About to set the event
        Not waiting this time
        Done
    """

    def __init__(self) -> None:
        self._value = False
        self._waiters = set()  # type: Set[Future[None]]

    def __repr__(self) -> str:
        return "<{} {}>".format(
            self.__class__.__name__,
            "set" if self.is_set() else "clear",
        )

    def is_set(self) -> bool:
        """Return ``True`` if the internal flag is true."""
        return self._value

    def set(self) -> None:
        """Set the internal flag to ``True``. All waiters are awakened.

        Calling `.wait` once the flag is set will not block.
        """
        if not self._value:
            self._value = True

            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(None)

    def clear(self) -> None:
        """Reset the internal flag to ``False``.

        Calls to `.wait` will block until `.set` is called.
        """
        self._value = False

    def wait(
        self, timeout: Optional[Union[float, datetime.timedelta]] = None
    ) -> Awaitable[None]:
        """Block until the internal flag is true.

        Returns an awaitable, which raises `tornado.util.TimeoutError` after a
        timeout.
        """
        fut = Future()  # type: Future[None]
        if self._value:
            fut.set_result(None)
            return fut
        self._waiters.add(fut)
        fut.add_done_callback(lambda fut: self._waiters.remove(fut))
        if timeout is None:
            return fut
        else:
            timeout_fut = gen.with_timeout(timeout, fut)
            # This is a slightly clumsy workaround for the fact that
            # gen.with_timeout doesn't cancel its futures. Cancelling
            # fut will remove it from the waiters list.
            timeout_fut.add_done_callback(
                lambda tf: fut.cancel() if not fut.done() else None
            )
            return timeout_fut


class _ReleasingContextManager:
    """Releases a Lock or Semaphore at the end of a "with" statement.

    with (yield semaphore.acquire()):
        pass

    # Now semaphore.release() has been called.
    """

    def __init__(self, obj: Any) -> None:
        self._obj = obj

    def __enter__(self) -> None:
```
