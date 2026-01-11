# Chunk: a5efc5aaf263_0

- source: `.venv-lab/Lib/site-packages/zmq/log/handlers.py`
- lines: 1-102
- chunk: 1/3

```
"""pyzmq logging handlers.

This mainly defines the PUBHandler object for publishing logging messages over
a zmq.PUB socket.

The PUBHandler can be used with the regular logging module, as in::

    >>> import logging
    >>> handler = PUBHandler('tcp://127.0.0.1:12345')
    >>> handler.root_topic = 'foo'
    >>> logger = logging.getLogger('foobar')
    >>> logger.setLevel(logging.DEBUG)
    >>> logger.addHandler(handler)

Or using ``dictConfig``, as in::

    >>> from logging.config import dictConfig
    >>> socket = Context.instance().socket(PUB)
    >>> socket.connect('tcp://127.0.0.1:12345')
    >>> dictConfig({
    >>>     'version': 1,
    >>>     'handlers': {
    >>>         'zmq': {
    >>>             'class': 'zmq.log.handlers.PUBHandler',
    >>>             'level': logging.DEBUG,
    >>>             'root_topic': 'foo',
    >>>             'interface_or_socket': socket
    >>>         }
    >>>     },
    >>>     'root': {
    >>>         'level': 'DEBUG',
    >>>         'handlers': ['zmq'],
    >>>     }
    >>> })


After this point, all messages logged by ``logger`` will be published on the
PUB socket.

Code adapted from StarCluster:

    https://github.com/jtriley/StarCluster/blob/StarCluster-0.91/starcluster/logger.py
"""

from __future__ import annotations

import logging
from copy import copy

import zmq

# Copyright (C) PyZMQ Developers
# Distributed under the terms of the Modified BSD License.


TOPIC_DELIM = "::"  # delimiter for splitting topics on the receiving end.


class PUBHandler(logging.Handler):
    """A basic logging handler that emits log messages through a PUB socket.

    Takes a PUB socket already bound to interfaces or an interface to bind to.

    Example::

        sock = context.socket(zmq.PUB)
        sock.bind('inproc://log')
        handler = PUBHandler(sock)

    Or::

        handler = PUBHandler('inproc://loc')

    These are equivalent.

    Log messages handled by this handler are broadcast with ZMQ topics
    ``this.root_topic`` comes first, followed by the log level
    (DEBUG,INFO,etc.), followed by any additional subtopics specified in the
    message by: log.debug("subtopic.subsub::the real message")
    """

    ctx: zmq.Context
    socket: zmq.Socket

    def __init__(
        self,
        interface_or_socket: str | zmq.Socket,
        context: zmq.Context | None = None,
        root_topic: str = '',
    ) -> None:
        logging.Handler.__init__(self)
        self.root_topic = root_topic
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                "%(levelname)s %(filename)s:%(lineno)d - %(message)s\n"
            ),
            logging.INFO: logging.Formatter("%(message)s\n"),
            logging.WARN: logging.Formatter(
                "%(levelname)s %(filename)s:%(lineno)d - %(message)s\n"
            ),
            logging.ERROR: logging.Formatter(
```
