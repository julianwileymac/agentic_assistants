# Chunk: 8bccfa19b5a5_3

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 258-360
- chunk: 4/7

```
anager:
    """Releases a Lock or Semaphore at the end of a "with" statement.

    with (yield semaphore.acquire()):
        pass

    # Now semaphore.release() has been called.
    """

    def __init__(self, obj: Any) -> None:
        self._obj = obj

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: "Optional[Type[BaseException]]",
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        self._obj.release()


class Semaphore(_TimeoutGarbageCollector):
    """A lock that can be acquired a fixed number of times before blocking.

    A Semaphore manages a counter representing the number of `.release` calls
    minus the number of `.acquire` calls, plus an initial value. The `.acquire`
    method blocks if necessary until it can return without making the counter
    negative.

    Semaphores limit access to a shared resource. To allow access for two
    workers at a time:

    .. testsetup:: semaphore

       from collections import deque

       from tornado import gen
       from tornado.ioloop import IOLoop
       from tornado.concurrent import Future

       inited = False

       async def simulator(futures):
           for f in futures:
               # simulate the asynchronous passage of time
               await gen.sleep(0)
               await gen.sleep(0)
               f.set_result(None)

       def use_some_resource():
           global inited
           global futures_q
           if not inited:
               inited = True
               # Ensure reliable doctest output: resolve Futures one at a time.
               futures_q = deque([Future() for _ in range(3)])
               IOLoop.current().add_callback(simulator, list(futures_q))

           return futures_q.popleft()

    .. testcode:: semaphore

        import asyncio
        from tornado import gen
        from tornado.locks import Semaphore

        sem = Semaphore(2)

        async def worker(worker_id):
            await sem.acquire()
            try:
                print("Worker %d is working" % worker_id)
                await use_some_resource()
            finally:
                print("Worker %d is done" % worker_id)
                sem.release()

        async def runner():
            # Join all workers.
            await gen.multi([worker(i) for i in range(3)])

        asyncio.run(runner())

    .. testoutput:: semaphore

        Worker 0 is working
        Worker 1 is working
        Worker 0 is done
        Worker 2 is working
        Worker 1 is done
        Worker 2 is done

    Workers 0 and 1 are allowed to run concurrently, but worker 2 waits until
    the semaphore has been released once, by worker 0.

    The semaphore can be used as an async context manager::

        async def worker(worker_id):
            async with sem:
```
