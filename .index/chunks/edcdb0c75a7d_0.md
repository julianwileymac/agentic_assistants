# Chunk: edcdb0c75a7d_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 1-90
- chunk: 1/20

```
import sys
import bisect
import types

from _pydev_bundle._pydev_saved_modules import threading
from _pydevd_bundle import pydevd_utils, pydevd_source_mapping
from _pydevd_bundle.pydevd_additional_thread_info import set_additional_thread_info
from _pydevd_bundle.pydevd_comm import (
    InternalGetThreadStack,
    internal_get_completions,
    InternalSetNextStatementThread,
    internal_reload_code,
    InternalGetVariable,
    InternalGetArray,
    InternalLoadFullValue,
    internal_get_description,
    internal_get_frame,
    internal_evaluate_expression,
    InternalConsoleExec,
    internal_get_variable_json,
    internal_change_variable,
    internal_change_variable_json,
    internal_evaluate_expression_json,
    internal_set_expression_json,
    internal_get_exception_details_json,
    internal_step_in_thread,
    internal_smart_step_into,
)
from _pydevd_bundle.pydevd_comm_constants import (
    CMD_THREAD_SUSPEND,
    file_system_encoding,
    CMD_STEP_INTO_MY_CODE,
    CMD_STOP_ON_START,
    CMD_SMART_STEP_INTO,
)
from _pydevd_bundle.pydevd_constants import (
    get_current_thread_id,
    set_protocol,
    get_protocol,
    HTTP_JSON_PROTOCOL,
    JSON_PROTOCOL,
    DebugInfoHolder,
    IS_WINDOWS,
    PYDEVD_USE_SYS_MONITORING,
)
from _pydevd_bundle.pydevd_net_command_factory_json import NetCommandFactoryJson
from _pydevd_bundle.pydevd_net_command_factory_xml import NetCommandFactory
import pydevd_file_utils
from _pydev_bundle import pydev_log
from _pydevd_bundle.pydevd_breakpoints import LineBreakpoint
from pydevd_tracing import get_exception_traceback_str
import os
import subprocess
import ctypes
from _pydevd_bundle.pydevd_collect_bytecode_info import code_to_bytecode_representation
import itertools
import linecache
from _pydevd_bundle.pydevd_utils import DAPGrouper, interrupt_main_thread
from _pydevd_bundle.pydevd_daemon_thread import run_as_pydevd_daemon_thread
from _pydevd_bundle.pydevd_thread_lifecycle import pydevd_find_thread_by_id, resume_threads
import tokenize
from _pydevd_sys_monitoring import pydevd_sys_monitoring

try:
    import dis
except ImportError:

    def _get_code_lines(code):
        raise NotImplementedError

else:

    def _get_code_lines(code):
        if not isinstance(code, types.CodeType):
            path = code
            with tokenize.open(path) as f:
                src = f.read()
            code = compile(src, path, "exec", 0, dont_inherit=True)
            return _get_code_lines(code)

        def iterate():
            # First, get all line starts for this code object. This does not include
            # bodies of nested class and function definitions, as they have their
            # own objects.
            for _, lineno in dis.findlinestarts(code):
                if lineno is not None:
                    yield lineno

            # For nested class and function definitions, their respective code objects
```
