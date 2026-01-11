# Chunk: fcd61ae4c7b1_0

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 1-86
- chunk: 1/6

```
"""A minimal application base mixin for all ZMQ based IPython frontends.

This is not a complete console app, as subprocess will not be able to receive
input, there is no real readline support, among other limitations. This is a
refactoring of what used to be the IPython/qt/console/qtconsoleapp.py
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import atexit
import os
import signal
import sys
import typing as t
import uuid
import warnings

from jupyter_core.application import base_aliases, base_flags
from traitlets import CBool, CUnicode, Dict, List, Type, Unicode
from traitlets.config.application import boolean_flag

from . import KernelManager, connect, find_connection_file, tunnel_to_kernel
from .blocking import BlockingKernelClient
from .connect import KernelConnectionInfo
from .kernelspec import NoSuchKernel
from .localinterfaces import localhost
from .restarter import KernelRestarter
from .session import Session
from .utils import _filefind

ConnectionFileMixin = connect.ConnectionFileMixin

# -----------------------------------------------------------------------------
# Aliases and Flags
# -----------------------------------------------------------------------------

flags: dict = {}
flags.update(base_flags)
# the flags that are specific to the frontend
# these must be scrubbed before being passed to the kernel,
# or it will raise an error on unrecognized flags
app_flags: dict = {
    "existing": (
        {"JupyterConsoleApp": {"existing": "kernel*.json"}},
        "Connect to an existing kernel. If no argument specified, guess most recent",
    ),
}
app_flags.update(
    boolean_flag(
        "confirm-exit",
        "JupyterConsoleApp.confirm_exit",
        """Set to display confirmation dialog on exit. You can always use 'exit' or
       'quit', to force a direct exit without any confirmation. This can also
       be set in the config file by setting
       `c.JupyterConsoleApp.confirm_exit`.
    """,
        """Don't prompt the user when exiting. This will terminate the kernel
       if it is owned by the frontend, and leave it alive if it is external.
       This can also be set in the config file by setting
       `c.JupyterConsoleApp.confirm_exit`.
    """,
    )
)
flags.update(app_flags)

aliases: dict = {}
aliases.update(base_aliases)

# also scrub aliases from the frontend
app_aliases: dict = {
    "ip": "JupyterConsoleApp.ip",
    "transport": "JupyterConsoleApp.transport",
    "hb": "JupyterConsoleApp.hb_port",
    "shell": "JupyterConsoleApp.shell_port",
    "iopub": "JupyterConsoleApp.iopub_port",
    "stdin": "JupyterConsoleApp.stdin_port",
    "control": "JupyterConsoleApp.control_port",
    "existing": "JupyterConsoleApp.existing",
    "f": "JupyterConsoleApp.connection_file",
    "kernel": "JupyterConsoleApp.kernel_name",
    "ssh": "JupyterConsoleApp.sshserver",
    "sshkey": "JupyterConsoleApp.sshkey",
}
aliases.update(app_aliases)
```
