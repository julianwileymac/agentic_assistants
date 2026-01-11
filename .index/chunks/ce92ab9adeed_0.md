# Chunk: ce92ab9adeed_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_console.py`
- lines: 1-76
- chunk: 1/4

```
"""An helper file for the pydev debugger (REPL) console
"""
import sys
import traceback
from _pydevd_bundle.pydevconsole_code import InteractiveConsole, _EvalAwaitInNewEventLoop
from _pydev_bundle import _pydev_completer
from _pydev_bundle.pydev_console_utils import BaseInterpreterInterface, BaseStdIn
from _pydev_bundle.pydev_imports import Exec
from _pydev_bundle.pydev_override import overrides
from _pydevd_bundle import pydevd_save_locals
from _pydevd_bundle.pydevd_io import IOBuf
from pydevd_tracing import get_exception_traceback_str
from _pydevd_bundle.pydevd_xml import make_valid_xml_value
import inspect
from _pydevd_bundle.pydevd_save_locals import update_globals_and_locals

CONSOLE_OUTPUT = "output"
CONSOLE_ERROR = "error"


# =======================================================================================================================
# ConsoleMessage
# =======================================================================================================================
class ConsoleMessage:
    """Console Messages"""

    def __init__(self):
        self.more = False
        # List of tuple [('error', 'error_message'), ('message_list', 'output_message')]
        self.console_messages = []

    def add_console_message(self, message_type, message):
        """add messages in the console_messages list"""
        for m in message.split("\n"):
            if m.strip():
                self.console_messages.append((message_type, m))

    def update_more(self, more):
        """more is set to true if further input is required from the user
        else more is set to false
        """
        self.more = more

    def to_xml(self):
        """Create an XML for console message_list, error and more (true/false)
        <xml>
            <message_list>console message_list</message_list>
            <error>console error</error>
            <more>true/false</more>
        </xml>
        """
        makeValid = make_valid_xml_value

        xml = "<xml><more>%s</more>" % (self.more)

        for message_type, message in self.console_messages:
            xml += '<%s message="%s"></%s>' % (message_type, makeValid(message), message_type)

        xml += "</xml>"

        return xml


# =======================================================================================================================
# _DebugConsoleStdIn
# =======================================================================================================================
class _DebugConsoleStdIn(BaseStdIn):
    @overrides(BaseStdIn.readline)
    def readline(self, *args, **kwargs):
        sys.stderr.write("Warning: Reading from stdin is still not supported in this console.\n")
        return "\n"


# =======================================================================================================================
# DebugConsole
```
