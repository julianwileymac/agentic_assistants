# Chunk: cc4c3c8aea41_0

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 1-104
- chunk: 1/14

```
"""A MultiKernelManager for use in the Jupyter server

- raises HTTPErrors
- creates REST API models
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import asyncio
import os
import pathlib  # noqa: TCH003
import sys
import typing as t
import warnings
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial, wraps

from jupyter_client.ioloop.manager import AsyncIOLoopKernelManager
from jupyter_client.multikernelmanager import AsyncMultiKernelManager, MultiKernelManager
from jupyter_client.session import Session
from jupyter_core.paths import exists
from jupyter_core.utils import ensure_async
from jupyter_events import EventLogger
from jupyter_events.schema_registry import SchemaRegistryException

if sys.version_info >= (3, 12):
    from typing import override
else:
    from overrides import overrides as override
from tornado import web
from tornado.concurrent import Future
from tornado.ioloop import IOLoop, PeriodicCallback
from traitlets import (
    Any,
    Bool,
    Dict,
    Float,
    Instance,
    Integer,
    List,
    TraitError,
    Unicode,
    default,
    validate,
)

from jupyter_server import DEFAULT_EVENTS_SCHEMA_PATH
from jupyter_server._tz import isoformat, utcnow
from jupyter_server.prometheus.metrics import KERNEL_CURRENTLY_RUNNING_TOTAL
from jupyter_server.utils import ApiPath, import_item, to_os_path


class MappingKernelManager(MultiKernelManager):
    """A KernelManager that handles
    - File mapping
    - HTTP error handling
    - Kernel message filtering
    """

    @default("kernel_manager_class")
    def _default_kernel_manager_class(self):
        return "jupyter_client.ioloop.IOLoopKernelManager"

    kernel_argv = List(Unicode())

    root_dir = Unicode(config=True)

    _kernel_connections = Dict()

    _kernel_ports: dict[str, list[int]] = Dict()  # type: ignore[assignment]

    _culler_callback = None

    _initialized_culler = False

    @default("root_dir")
    def _default_root_dir(self):
        if not self.parent:
            return os.getcwd()
        return self.parent.root_dir

    @validate("root_dir")
    def _update_root_dir(self, proposal):
        """Do a bit of validation of the root dir."""
        value = proposal["value"]
        if not os.path.isabs(value):
            # If we receive a non-absolute path, make it absolute.
            value = os.path.abspath(value)
        if not exists(value) or not os.path.isdir(value):
            raise TraitError("kernel root dir %r is not a directory" % value)
        return value

    cull_idle_timeout = Integer(
        0,
        config=True,
        help="""Timeout (in seconds) after which a kernel is considered idle and ready to be culled.
        Values of 0 or lower disable culling. Very short timeouts may result in kernels being culled
        for users with poor network connections.""",
    )
```
