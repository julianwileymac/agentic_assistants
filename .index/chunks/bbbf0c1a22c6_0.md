# Chunk: bbbf0c1a22c6_0

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 1-98
- chunk: 1/9

```
# Derived from iostream.py from tornado 1.0, Copyright 2009 Facebook
# Used under Apache License Version 2.0
#
# Modifications are Copyright (C) PyZMQ Developers
# Distributed under the terms of the Modified BSD License.
"""A utility class for event-based messaging on a zmq socket using tornado.

.. seealso::

    - :mod:`zmq.asyncio`
    - :mod:`zmq.eventloop.future`
"""

from __future__ import annotations

import asyncio
import pickle
import warnings
from queue import Queue
from typing import Any, Awaitable, Callable, Literal, Sequence, cast, overload

from tornado.ioloop import IOLoop
from tornado.log import gen_log

import zmq
import zmq._future
from zmq import POLLIN, POLLOUT
from zmq.utils import jsonapi


class ZMQStream:
    """A utility class to register callbacks when a zmq socket sends and receives

    For use with tornado IOLoop.

    There are three main methods

    Methods:

    * **on_recv(callback, copy=True):**
        register a callback to be run every time the socket has something to receive
    * **on_send(callback):**
        register a callback to be run every time you call send
    * **send_multipart(self, msg, flags=0, copy=False, callback=None):**
        perform a send that will trigger the callback
        if callback is passed, on_send is also called.

        There are also send_multipart(), send_json(), send_pyobj()

    Three other methods for deactivating the callbacks:

    * **stop_on_recv():**
        turn off the recv callback
    * **stop_on_send():**
        turn off the send callback

    which simply call ``on_<evt>(None)``.

    The entire socket interface, excluding direct recv methods, is also
    provided, primarily through direct-linking the methods.
    e.g.

    >>> stream.bind is stream.socket.bind
    True


    .. versionadded:: 25

        send/recv callbacks can be coroutines.

    .. versionchanged:: 25

        ZMQStreams only support base zmq.Socket classes (this has always been true, but not enforced).
        If ZMQStreams are created with e.g. async Socket subclasses,
        a RuntimeWarning will be shown,
        and the socket cast back to the default zmq.Socket
        before connecting events.

        Previously, using async sockets (or any zmq.Socket subclass) would result in undefined behavior for the
        arguments passed to callback functions.
        Now, the callback functions reliably get the return value of the base `zmq.Socket` send/recv_multipart methods
        (the list of message frames).
    """

    socket: zmq.Socket
    io_loop: IOLoop
    poller: zmq.Poller
    _send_queue: Queue
    _recv_callback: Callable | None
    _send_callback: Callable | None
    _close_callback: Callable | None
    _state: int = 0
    _flushed: bool = False
    _recv_copy: bool = False
    _fd: int

    def __init__(self, socket: zmq.Socket, io_loop: IOLoop | None = None):
```
