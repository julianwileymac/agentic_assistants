# Chunk: fcd659aef1e5_0

- source: `.venv-lab/Lib/site-packages/tornado/util.py`
- lines: 1-95
- chunk: 1/6

```
"""Miscellaneous utility functions and classes.

This module is used internally by Tornado.  It is not necessarily expected
that the functions and classes defined here will be useful to other
applications, but they are documented here in case they are.

The one public-facing part of this module is the `Configurable` class
and its `~Configurable.configure` method, which becomes a part of the
interface of its subclasses, including `.AsyncHTTPClient`, `.IOLoop`,
and `.Resolver`.
"""

import array
import asyncio
from inspect import getfullargspec
import os
import re
import typing
import zlib

from typing import (
    Any,
    Optional,
    Dict,
    Mapping,
    List,
    Tuple,
    Match,
    Callable,
    Type,
    Sequence,
)

if typing.TYPE_CHECKING:
    # Additional imports only used in type comments.
    # This lets us make these imports lazy.
    import datetime  # noqa: F401
    from types import TracebackType  # noqa: F401
    from typing import Union  # noqa: F401
    import unittest  # noqa: F401

# Aliases for types that are spelled differently in different Python
# versions. bytes_type is deprecated and no longer used in Tornado
# itself but is left in case anyone outside Tornado is using it.
bytes_type = bytes
unicode_type = str
basestring_type = str


# versionchanged:: 6.2
# no longer our own TimeoutError, use standard asyncio class
TimeoutError = asyncio.TimeoutError


class ObjectDict(Dict[str, Any]):
    """Makes a dictionary behave like an object, with attribute-style access."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class GzipDecompressor:
    """Streaming gzip decompressor.

    The interface is like that of `zlib.decompressobj` (without some of the
    optional arguments, but it understands gzip headers and checksums.
    """

    def __init__(self) -> None:
        # Magic parameter makes zlib module understand gzip header
        # http://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
        # This works on cpython and pypy, but not jython.
        self.decompressobj = zlib.decompressobj(16 + zlib.MAX_WBITS)

    def decompress(self, value: bytes, max_length: int = 0) -> bytes:
        """Decompress a chunk, returning newly-available data.

        Some data may be buffered for later processing; `flush` must
        be called when there is no more input data to ensure that
        all data was processed.

        If ``max_length`` is given, some input data may be left over
        in ``unconsumed_tail``; you must retrieve this value and pass
        it back to a future call to `decompress` if it is not empty.
        """
        return self.decompressobj.decompress(value, max_length)

    @property
```
