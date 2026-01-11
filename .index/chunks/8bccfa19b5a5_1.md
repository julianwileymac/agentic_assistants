# Chunk: 8bccfa19b5a5_1

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 85-178
- chunk: 2/7

```
:

        I'll wait right here
        About to notify
        Done notifying
        I'm done waiting

    `wait` takes an optional ``timeout`` argument, which is either an absolute
    timestamp::

        io_loop = IOLoop.current()

        # Wait up to 1 second for a notification.
        await condition.wait(timeout=io_loop.time() + 1)

    ...or a `datetime.timedelta` for a timeout relative to the current time::

        # Wait up to 1 second.
        await condition.wait(timeout=datetime.timedelta(seconds=1))

    The method returns False if there's no notification before the deadline.

    .. versionchanged:: 5.0
       Previously, waiters could be notified synchronously from within
       `notify`. Now, the notification will always be received on the
       next iteration of the `.IOLoop`.
    """

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}"
        if self._waiters:
            result += " waiters[%s]" % len(self._waiters)
        return result + ">"

    def wait(
        self, timeout: Optional[Union[float, datetime.timedelta]] = None
    ) -> Awaitable[bool]:
        """Wait for `.notify`.

        Returns a `.Future` that resolves ``True`` if the condition is notified,
        or ``False`` after a timeout.
        """
        waiter = Future()  # type: Future[bool]
        self._waiters.append(waiter)
        if timeout:

            def on_timeout() -> None:
                if not waiter.done():
                    future_set_result_unless_cancelled(waiter, False)
                self._garbage_collect()

            io_loop = ioloop.IOLoop.current()
            timeout_handle = io_loop.add_timeout(timeout, on_timeout)
            waiter.add_done_callback(lambda _: io_loop.remove_timeout(timeout_handle))
        return waiter

    def notify(self, n: int = 1) -> None:
        """Wake ``n`` waiters."""
        waiters = []  # Waiters we plan to run right now.
        while n and self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():  # Might have timed out.
                n -= 1
                waiters.append(waiter)

        for waiter in waiters:
            future_set_result_unless_cancelled(waiter, True)

    def notify_all(self) -> None:
        """Wake all waiters."""
        self.notify(len(self._waiters))


class Event:
    """An event blocks coroutines until its internal flag is set to True.

    Similar to `threading.Event`.

    A coroutine can wait for an event to be set. Once it is set, calls to
    ``yield event.wait()`` will not block unless the event has been cleared:

    .. testcode::

        import asyncio
        from tornado import gen
        from tornado.locks import Event

        event = Event()

        async def waiter():
            print("Waiting for event")
            await event.wait()
            print("Not waiting this time")
```
