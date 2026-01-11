# Chunk: eb4bf5d6ad95_0

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 1-92
- chunk: 1/8

```
"""
Makes it possible to do the compiled analysis in a subprocess. This has two
goals:

1. Making it safer - Segfaults and RuntimeErrors as well as stdout/stderr can
   be ignored and dealt with.
2. Make it possible to handle different Python versions as well as virtualenvs.

The architecture here is briefly:
 - For each Jedi `Environment` there is a corresponding subprocess which
   operates within the target environment. If the subprocess dies it is replaced
   at this level.
 - `CompiledSubprocess` manages exactly one subprocess and handles communication
   from the parent side.
 - `Listener` runs within the subprocess, processing each request and yielding
   results.
 - `InterpreterEnvironment` provides an API which matches that of `Environment`,
   but runs functionality inline rather than within a subprocess. It is thus
   used both directly in places where a subprocess is unnecessary and/or
   undesirable and also within subprocesses themselves.
 - `InferenceStateSubprocess` (or `InferenceStateSameProcess`) provide high
   level access to functionality within the subprocess from within the parent.
   Each `InterpreterState` has an instance of one of these, provided by its
   environment.
"""

import collections
import os
import sys
import queue
import subprocess
import traceback
import weakref
from functools import partial
from threading import Thread
from typing import Dict, TYPE_CHECKING

from jedi._compatibility import pickle_dump, pickle_load
from jedi import debug
from jedi.cache import memoize_method
from jedi.inference.compiled.subprocess import functions
from jedi.inference.compiled.access import DirectObjectAccess, AccessPath, \
    SignatureParam
from jedi.api.exceptions import InternalError

if TYPE_CHECKING:
    from jedi.inference import InferenceState


_MAIN_PATH = os.path.join(os.path.dirname(__file__), '__main__.py')
PICKLE_PROTOCOL = 4


def _GeneralizedPopen(*args, **kwargs):
    if os.name == 'nt':
        try:
            # Was introduced in Python 3.7.
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
        except AttributeError:
            CREATE_NO_WINDOW = 0x08000000
        kwargs['creationflags'] = CREATE_NO_WINDOW
    # The child process doesn't need file descriptors except 0, 1, 2.
    # This is unix only.
    kwargs['close_fds'] = 'posix' in sys.builtin_module_names

    return subprocess.Popen(*args, **kwargs)


def _enqueue_output(out, queue_):
    for line in iter(out.readline, b''):
        queue_.put(line)


def _add_stderr_to_debug(stderr_queue):
    while True:
        # Try to do some error reporting from the subprocess and print its
        # stderr contents.
        try:
            line = stderr_queue.get_nowait()
            line = line.decode('utf-8', 'replace')
            debug.warning('stderr output: %s' % line.rstrip('\n'))
        except queue.Empty:
            break


def _get_function(name):
    return getattr(functions, name)


def _cleanup_process(process, thread):
    try:
```
