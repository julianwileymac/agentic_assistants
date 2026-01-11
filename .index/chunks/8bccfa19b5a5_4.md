# Chunk: 8bccfa19b5a5_4

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 350-435
- chunk: 5/7

```
one
        Worker 2 is done

    Workers 0 and 1 are allowed to run concurrently, but worker 2 waits until
    the semaphore has been released once, by worker 0.

    The semaphore can be used as an async context manager::

        async def worker(worker_id):
            async with sem:
                print("Worker %d is working" % worker_id)
                await use_some_resource()

            # Now the semaphore has been released.
            print("Worker %d is done" % worker_id)

    For compatibility with older versions of Python, `.acquire` is a
    context manager, so ``worker`` could also be written as::

        @gen.coroutine
        def worker(worker_id):
            with (yield sem.acquire()):
                print("Worker %d is working" % worker_id)
                yield use_some_resource()

            # Now the semaphore has been released.
            print("Worker %d is done" % worker_id)

    .. versionchanged:: 4.3
       Added ``async with`` support in Python 3.5.

    """

    def __init__(self, value: int = 1) -> None:
        super().__init__()
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")

        self._value = value

    def __repr__(self) -> str:
        res = super().__repr__()
        extra = "locked" if self._value == 0 else f"unlocked,value:{self._value}"
        if self._waiters:
            extra = f"{extra},waiters:{len(self._waiters)}"
        return f"<{res[1:-1]} [{extra}]>"

    def release(self) -> None:
        """Increment the counter and wake one waiter."""
        self._value += 1
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                self._value -= 1

                # If the waiter is a coroutine paused at
                #
                #     with (yield semaphore.acquire()):
                #
                # then the context manager's __exit__ calls release() at the end
                # of the "with" block.
                waiter.set_result(_ReleasingContextManager(self))
                break

    def acquire(
        self, timeout: Optional[Union[float, datetime.timedelta]] = None
    ) -> Awaitable[_ReleasingContextManager]:
        """Decrement the counter. Returns an awaitable.

        Block if the counter is zero and wait for a `.release`. The awaitable
        raises `.TimeoutError` after the deadline.
        """
        waiter = Future()  # type: Future[_ReleasingContextManager]
        if self._value > 0:
            self._value -= 1
            waiter.set_result(_ReleasingContextManager(self))
        else:
            self._waiters.append(waiter)
            if timeout:

                def on_timeout() -> None:
                    if not waiter.done():
                        waiter.set_exception(gen.TimeoutError())
                    self._garbage_collect()

```
