# Chunk: db6cddaa5f29_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 1-95
- chunk: 1/8

```
"""
Entry point module to start the interactive console.
"""
from _pydev_bundle._pydev_saved_modules import thread, _code
from _pydevd_bundle.pydevd_constants import IS_JYTHON

start_new_thread = thread.start_new_thread

from _pydevd_bundle.pydevconsole_code import InteractiveConsole

compile_command = _code.compile_command
InteractiveInterpreter = _code.InteractiveInterpreter

import os
import sys

from _pydev_bundle._pydev_saved_modules import threading
from _pydevd_bundle.pydevd_constants import INTERACTIVE_MODE_AVAILABLE

import traceback
from _pydev_bundle import pydev_log

from _pydevd_bundle import pydevd_save_locals

from _pydev_bundle.pydev_imports import Exec, _queue

import builtins as __builtin__

from _pydev_bundle.pydev_console_utils import BaseInterpreterInterface, BaseStdIn  # @UnusedImport
from _pydev_bundle.pydev_console_utils import CodeFragment


class Command:
    def __init__(self, interpreter, code_fragment):
        """
        :type code_fragment: CodeFragment
        :type interpreter: InteractiveConsole
        """
        self.interpreter = interpreter
        self.code_fragment = code_fragment
        self.more = None

    def symbol_for_fragment(code_fragment):
        if code_fragment.is_single_line:
            symbol = "single"
        else:
            if IS_JYTHON:
                symbol = "single"  # Jython doesn't support exec
            else:
                symbol = "exec"
        return symbol

    symbol_for_fragment = staticmethod(symbol_for_fragment)

    def run(self):
        text = self.code_fragment.text
        symbol = self.symbol_for_fragment(self.code_fragment)

        self.more = self.interpreter.runsource(text, "<input>", symbol)


try:
    from _pydev_bundle.pydev_imports import execfile

    __builtin__.execfile = execfile
except:
    pass

# Pull in runfile, the interface to UMD that wraps execfile
from _pydev_bundle.pydev_umd import runfile, _set_globals_function

if sys.version_info[0] >= 3:
    __builtin__.runfile = runfile
else:
    __builtin__.runfile = runfile


# =======================================================================================================================
# InterpreterInterface
# =======================================================================================================================
class InterpreterInterface(BaseInterpreterInterface):
    """
    The methods in this class should be registered in the xml-rpc server.
    """

    def __init__(self, host, client_port, mainThread, connect_status_queue=None):
        BaseInterpreterInterface.__init__(self, mainThread, connect_status_queue)
        self.client_port = client_port
        self.host = host
        self.namespace = {}
        self.interpreter = InteractiveConsole(self.namespace)
        self._input_error_printed = False

    def do_add_exec(self, codeFragment):
```
