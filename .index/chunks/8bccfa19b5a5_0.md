# Chunk: 8bccfa19b5a5_0

- source: `.venv-lab/Lib/site-packages/tornado/locks.py`
- lines: 1-98
- chunk: 1/7

```
# Copyright 2015 The Tornado Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections
import datetime
import types

from tornado import gen, ioloop
from tornado.concurrent import Future, future_set_result_unless_cancelled

from typing import Union, Optional, Type, Any, Awaitable
import typing

if typing.TYPE_CHECKING:
    from typing import Deque, Set  # noqa: F401

__all__ = ["Condition", "Event", "Semaphore", "BoundedSemaphore", "Lock"]


class _TimeoutGarbageCollector:
    """Base class for objects that periodically clean up timed-out waiters.

    Avoids memory leak in a common pattern like:

        while True:
            yield condition.wait(short_timeout)
            print('looping....')
    """

    def __init__(self) -> None:
        self._waiters = collections.deque()  # type: Deque[Future]
        self._timeouts = 0

    def _garbage_collect(self) -> None:
        # Occasionally clear timed-out waiters.
        self._timeouts += 1
        if self._timeouts > 100:
            self._timeouts = 0
            self._waiters = collections.deque(w for w in self._waiters if not w.done())


class Condition(_TimeoutGarbageCollector):
    """A condition allows one or more coroutines to wait until notified.

    Like a standard `threading.Condition`, but does not need an underlying lock
    that is acquired and released.

    With a `Condition`, coroutines can wait to be notified by other coroutines:

    .. testcode::

        import asyncio
        from tornado import gen
        from tornado.locks import Condition

        condition = Condition()

        async def waiter():
            print("I'll wait right here")
            await condition.wait()
            print("I'm done waiting")

        async def notifier():
            print("About to notify")
            condition.notify()
            print("Done notifying")

        async def runner():
            # Wait for waiter() and notifier() in parallel
            await gen.multi([waiter(), notifier()])

        asyncio.run(runner())

    .. testoutput::

        I'll wait right here
        About to notify
        Done notifying
        I'm done waiting

    `wait` takes an optional ``timeout`` argument, which is either an absolute
    timestamp::

        io_loop = IOLoop.current()

        # Wait up to 1 second for a notification.
```
