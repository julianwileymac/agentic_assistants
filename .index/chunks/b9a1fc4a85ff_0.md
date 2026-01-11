# Chunk: b9a1fc4a85ff_0

- source: `.venv-lab/Lib/site-packages/jupyter_client/channels.py`
- lines: 1-101
- chunk: 1/4

```
"""Base classes to manage a Client's interaction with a running kernel"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import asyncio
import atexit
import time
import typing as t
from queue import Empty
from threading import Event, Thread

import zmq.asyncio
from jupyter_core.utils import ensure_async

from ._version import protocol_version_info
from .channelsabc import HBChannelABC
from .session import Session

# import ZMQError in top-level namespace, to avoid ugly attribute-error messages
# during garbage collection of threads at exit

# -----------------------------------------------------------------------------
# Constants and exceptions
# -----------------------------------------------------------------------------

major_protocol_version = protocol_version_info[0]


class InvalidPortNumber(Exception):  # noqa
    """An exception raised for an invalid port number."""

    pass


class HBChannel(Thread):
    """The heartbeat channel which monitors the kernel heartbeat.

    Note that the heartbeat channel is paused by default. As long as you start
    this channel, the kernel manager will ensure that it is paused and un-paused
    as appropriate.
    """

    session = None
    socket = None
    address = None
    _exiting = False

    time_to_dead: float = 1.0
    _running = None
    _pause = None
    _beating = None

    def __init__(
        self,
        context: zmq.Context | None = None,
        session: Session | None = None,
        address: t.Union[t.Tuple[str, int], str] = "",
    ) -> None:
        """Create the heartbeat monitor thread.

        Parameters
        ----------
        context : :class:`zmq.Context`
            The ZMQ context to use.
        session : :class:`session.Session`
            The session to use.
        address : zmq url
            Standard (ip, port) tuple that the kernel is listening on.
        """
        super().__init__()
        self.daemon = True

        self.context = context
        self.session = session
        if isinstance(address, tuple):
            if address[1] == 0:
                message = "The port number for a channel cannot be 0."
                raise InvalidPortNumber(message)
            address_str = "tcp://%s:%i" % address
        else:
            address_str = address
        self.address = address_str

        # running is False until `.start()` is called
        self._running = False
        self._exit = Event()
        # don't start paused
        self._pause = False
        self.poller = zmq.Poller()

    @staticmethod
    @atexit.register
    def _notice_exit() -> None:
        # Class definitions can be torn down during interpreter shutdown.
        # We only need to set _exiting flag if this hasn't happened.
        if HBChannel is not None:
            HBChannel._exiting = True

    def _create_socket(self) -> None:
        if self.socket is not None:
```
