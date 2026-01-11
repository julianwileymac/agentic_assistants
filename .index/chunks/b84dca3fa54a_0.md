# Chunk: b84dca3fa54a_0

- source: `.venv-lab/Lib/site-packages/jupyter_console/app.py`
- lines: 1-94
- chunk: 1/2

```
""" A minimal application using the ZMQ-based terminal IPython frontend.

This is not a complete console app, as subprocess will not be able to receive
input, there is no real readline support, among other limitations.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import signal
import sys

from traitlets import (
    Dict, Any
)
from traitlets.config import catch_config_error, boolean_flag

from jupyter_core.application import JupyterApp, base_aliases, base_flags
from jupyter_client.consoleapp import (
        JupyterConsoleApp, app_aliases, app_flags,
    )

from jupyter_console.ptshell import ZMQTerminalInteractiveShell
from jupyter_console import __version__

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

_examples = """
jupyter console # start the ZMQ-based console
jupyter console --existing # connect to an existing ipython session
"""

#-----------------------------------------------------------------------------
# Flags and Aliases
#-----------------------------------------------------------------------------

# copy flags from mixin:
flags = dict(base_flags)
# start with mixin frontend flags:
# update full dict with frontend flags:
flags.update(app_flags)
flags.update(boolean_flag(
    'simple-prompt', 'ZMQTerminalInteractiveShell.simple_prompt',
    "Force simple minimal prompt using `raw_input`",
    "Use a rich interactive prompt with prompt_toolkit"
))

# copy flags from mixin
aliases = dict(base_aliases)

aliases.update(app_aliases)

frontend_aliases = set(app_aliases.keys())
frontend_flags = set(app_flags.keys())


#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------


class ZMQTerminalIPythonApp(JupyterApp, JupyterConsoleApp):  # type:ignore[misc]
    name = "jupyter-console"
    version = __version__
    """Start a terminal frontend to the IPython zmq kernel."""

    description = """
        The Jupyter terminal-based Console.

        This launches a Console application inside a terminal.

        The Console supports various extra features beyond the traditional
        single-process Terminal IPython shell, such as connecting to an
        existing ipython session, via:

            jupyter console --existing

        where the previous session could have been created by another ipython
        console, an ipython qtconsole, or by opening an ipython notebook.

    """
    examples = _examples

    classes = [ZMQTerminalInteractiveShell] + JupyterConsoleApp.classes  # type:ignore[operator]
    flags = Dict(flags)  # type:ignore[assignment]
    aliases = Dict(aliases)  # type:ignore[assignment]
    frontend_aliases = Any(frontend_aliases)
    frontend_flags = Any(frontend_flags)
```
