# Chunk: fcda211deb9c_0

- source: `.venv-lab/Lib/site-packages/debugpy/adapter/servers.py`
- lines: 1-99
- chunk: 1/9

```
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time

import debugpy
from debugpy import adapter
from debugpy.common import json, log, messaging, sockets
from debugpy.adapter import components, sessions
import traceback
import io

access_token = None
"""Access token used to authenticate with the servers."""

listener = None
"""Listener socket that accepts server connections."""

_lock = threading.RLock()

_connections = []
"""All servers that are connected to this adapter, in order in which they connected.
"""

_connections_changed = threading.Event()


class Connection(object):
    """A debug server that is connected to the adapter.

    Servers that are not participating in a debug session are managed directly by the
    corresponding Connection instance.

    Servers that are participating in a debug session are managed by that sessions's
    Server component instance, but Connection object remains, and takes over again
    once the session ends.
    """

    disconnected: bool

    process_replaced: bool
    """Whether this is a connection to a process that is being replaced in situ
    by another process, e.g. via exec().
    """

    server: Server | None
    """The Server component, if this debug server belongs to Session.
    """

    pid: int | None

    ppid: int | None

    channel: messaging.JsonMessageChannel

    def __init__(self, sock):
        from debugpy.adapter import sessions

        self.disconnected = False

        self.process_replaced = False

        self.server = None

        self.pid = None

        stream = messaging.JsonIOStream.from_socket(sock, str(self))
        self.channel = messaging.JsonMessageChannel(stream, self)
        self.channel.start()

        try:
            self.authenticate()
            info = self.channel.request("pydevdSystemInfo")
            process_info = info("process", json.object())
            self.pid = process_info("pid", int)
            self.ppid = process_info("ppid", int, optional=True)
            if self.ppid == ():
                self.ppid = None
            self.channel.name = stream.name = str(self)

            with _lock:
                # The server can disconnect concurrently before we get here, e.g. if
                # it was force-killed. If the disconnect() handler has already run,
                # don't register this server or report it, since there's nothing to
                # deregister it.
                if self.disconnected:
                    return

                # An existing connection with the same PID and process_replaced == True
                # corresponds to the process that replaced itself with this one, so it's
                # not an error.
```
