# Chunk: 6f3dcfe8cb9a_0

- source: `.venv-lab/Lib/site-packages/IPython/utils/_process_common.py`
- lines: 1-80
- chunk: 1/3

```
"""Common utilities for the various process_* implementations.

This file is only meant to be imported by the platform-specific implementations
of subprocess utilities, and it contains tools that are common to all of them.
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2010-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import shlex
import subprocess
import sys
from typing import IO, Any, List, Union
from collections.abc import Callable

from IPython.utils import py3compat

#-----------------------------------------------------------------------------
# Function definitions
#-----------------------------------------------------------------------------

def read_no_interrupt(stream: IO[Any]) -> bytes:
    """Read from a pipe ignoring EINTR errors.

    This is necessary because when reading from pipes with GUI event loops
    running in the background, often interrupts are raised that stop the
    command from completing."""
    import errno

    try:
        return stream.read()
    except IOError as err:
        if err.errno != errno.EINTR:
            raise


def process_handler(
    cmd: Union[str, List[str]],
    callback: Callable[[subprocess.Popen], int | str | bytes],
    stderr=subprocess.PIPE,
) -> int | str | bytes:
    """Open a command in a shell subprocess and execute a callback.

    This function provides common scaffolding for creating subprocess.Popen()
    calls.  It creates a Popen object and then calls the callback with it.

    Parameters
    ----------
    cmd : str or list
        A command to be executed by the system, using :class:`subprocess.Popen`.
        If a string is passed, it will be run in the system shell. If a list is
        passed, it will be used directly as arguments.
    callback : callable
        A one-argument function that will be called with the Popen object.
    stderr : file descriptor number, optional
        By default this is set to ``subprocess.PIPE``, but you can also pass the
        value ``subprocess.STDOUT`` to force the subprocess' stderr to go into
        the same file descriptor as its stdout.  This is useful to read stdout
        and stderr combined in the order they are generated.

    Returns
    -------
    The return value of the provided callback is returned.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    # On win32, close_fds can't be true when using pipes for stdin/out/err
    if sys.platform == "win32" and stderr != subprocess.PIPE:
        close_fds = False
    else:
        close_fds = True
```
