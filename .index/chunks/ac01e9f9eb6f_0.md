# Chunk: ac01e9f9eb6f_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 1-72
- chunk: 1/9

```
import os
import sys
import traceback
from _pydev_bundle.pydev_imports import xmlrpclib, _queue, Exec
from _pydev_bundle._pydev_calltip_util import get_description
from _pydevd_bundle import pydevd_vars
from _pydevd_bundle import pydevd_xml
from _pydevd_bundle.pydevd_constants import IS_JYTHON, NEXT_VALUE_SEPARATOR, get_global_debugger, silence_warnings_decorator
from contextlib import contextmanager
from _pydev_bundle import pydev_log
from _pydevd_bundle.pydevd_utils import interrupt_main_thread

from io import StringIO


# =======================================================================================================================
# BaseStdIn
# =======================================================================================================================
class BaseStdIn:
    def __init__(self, original_stdin=sys.stdin, *args, **kwargs):
        try:
            self.encoding = sys.stdin.encoding
        except:
            # Not sure if it's available in all Python versions...
            pass
        self.original_stdin = original_stdin

        try:
            self.errors = sys.stdin.errors  # Who knew? sys streams have an errors attribute!
        except:
            # Not sure if it's available in all Python versions...
            pass

    def readline(self, *args, **kwargs):
        # sys.stderr.write('Cannot readline out of the console evaluation\n') -- don't show anything
        # This could happen if the user had done input('enter number).<-- upon entering this, that message would appear,
        # which is not something we want.
        return "\n"

    def write(self, *args, **kwargs):
        pass  # not available StdIn (but it can be expected to be in the stream interface)

    def flush(self, *args, **kwargs):
        pass  # not available StdIn (but it can be expected to be in the stream interface)

    def read(self, *args, **kwargs):
        # in the interactive interpreter, a read and a readline are the same.
        return self.readline()

    def close(self, *args, **kwargs):
        pass  # expected in StdIn

    def __iter__(self):
        # BaseStdIn would not be considered as Iterable in Python 3 without explicit `__iter__` implementation
        return self.original_stdin.__iter__()

    def __getattr__(self, item):
        # it's called if the attribute wasn't found
        if hasattr(self.original_stdin, item):
            return getattr(self.original_stdin, item)
        raise AttributeError("%s has no attribute %s" % (self.original_stdin, item))


# =======================================================================================================================
# StdIn
# =======================================================================================================================
class StdIn(BaseStdIn):
    """
    Object to be added to stdin (to emulate it as non-blocking while the next line arrives)
    """

```
