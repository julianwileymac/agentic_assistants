# Chunk: 6ca3aacfcc2f_0

- source: `.venv-lab/Lib/site-packages/psutil/_psposix.py`
- lines: 1-103
- chunk: 1/3

```
# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Routines common to all posix systems."""

import enum
import glob
import os
import signal
import time

from . import _ntuples as ntp
from ._common import MACOS
from ._common import TimeoutExpired
from ._common import memoize
from ._common import usage_percent

if MACOS:
    from . import _psutil_osx


__all__ = ['pid_exists', 'wait_pid', 'disk_usage', 'get_terminal_map']


def pid_exists(pid):
    """Check whether pid exists in the current process table."""
    if pid == 0:
        # According to "man 2 kill" PID 0 has a special meaning:
        # it refers to <<every process in the process group of the
        # calling process>> so we don't want to go any further.
        # If we get here it means this UNIX platform *does* have
        # a process with id 0.
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # EPERM clearly means there's a process to deny access to
        return True
    # According to "man 2 kill" possible error values are
    # (EINVAL, EPERM, ESRCH)
    else:
        return True


Negsignal = enum.IntEnum(
    'Negsignal', {x.name: -x.value for x in signal.Signals}
)


def negsig_to_enum(num):
    """Convert a negative signal value to an enum."""
    try:
        return Negsignal(num)
    except ValueError:
        return num


def wait_pid(
    pid,
    timeout=None,
    proc_name=None,
    _waitpid=os.waitpid,
    _timer=getattr(time, 'monotonic', time.time),  # noqa: B008
    _min=min,
    _sleep=time.sleep,
    _pid_exists=pid_exists,
):
    """Wait for a process PID to terminate.

    If the process terminated normally by calling exit(3) or _exit(2),
    or by returning from main(), the return value is the positive integer
    passed to *exit().

    If it was terminated by a signal it returns the negated value of the
    signal which caused the termination (e.g. -SIGTERM).

    If PID is not a children of os.getpid() (current process) just
    wait until the process disappears and return None.

    If PID does not exist at all return None immediately.

    If *timeout* != None and process is still alive raise TimeoutExpired.
    timeout=0 is also possible (either return immediately or raise).
    """
    if pid <= 0:
        # see "man waitpid"
        msg = "can't wait for PID 0"
        raise ValueError(msg)
    interval = 0.0001
    flags = 0
    if timeout is not None:
        flags |= os.WNOHANG
        stop_at = _timer() + timeout

    def sleep(interval):
        # Sleep for some time and return a new increased interval.
        if timeout is not None:
            if _timer() >= stop_at:
                raise TimeoutExpired(timeout, pid=pid, name=proc_name)
```
