# Chunk: 7e6f1b19fdab_0

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 1-88
- chunk: 1/8

```
# encoding: utf-8
"""
A mixin for :class:`~IPython.core.application.Application` classes that
launch InteractiveShell instances, load extensions, etc.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import glob
from itertools import chain
import os
import sys
import typing as t

from traitlets.config.application import boolean_flag
from traitlets.config.configurable import Configurable
from traitlets.config.loader import Config
from IPython.core.application import SYSTEM_CONFIG_DIRS, ENV_CONFIG_DIRS
from IPython.utils.contexts import preserve_keys
from IPython.utils.path import filefind
from traitlets import (
    Unicode,
    Instance,
    List,
    Bool,
    CaselessStrEnum,
    observe,
    DottedObjectName,
    Undefined,
)
from IPython.terminal import pt_inputhooks

# -----------------------------------------------------------------------------
# Aliases and Flags
# -----------------------------------------------------------------------------

gui_keys = tuple(sorted(pt_inputhooks.backends) + sorted(pt_inputhooks.aliases))

shell_flags = {}

addflag = lambda *args: shell_flags.update(boolean_flag(*args))
addflag(
    "autoindent",
    "InteractiveShell.autoindent",
    "Turn on autoindenting.",
    "Turn off autoindenting.",
)
addflag(
    "automagic",
    "InteractiveShell.automagic",
    """Turn on the auto calling of magic commands. Type %%magic at the
        IPython  prompt  for  more information.""",
        'Turn off the auto calling of magic commands.'
)
addflag('pdb', 'InteractiveShell.pdb',
    "Enable auto calling the pdb debugger after every exception.",
    "Disable auto calling the pdb debugger after every exception."
)
addflag('pprint', 'PlainTextFormatter.pprint',
    "Enable auto pretty printing of results.",
    "Disable auto pretty printing of results."
)
addflag('color-info', 'InteractiveShell.color_info',
    """IPython can display information about objects via a set of functions,
    and optionally can use colors for this, syntax highlighting
    source code and various other elements. This is on by default, but can cause
    problems with some pagers. If you see such problems, you can disable the
    colours.""",
    "Disable using colors for info related things."
)
addflag('ignore-cwd', 'InteractiveShellApp.ignore_cwd',
        "Exclude the current working directory from sys.path",
        "Include the current working directory in sys.path",
)
nosep_config = Config()
nosep_config.InteractiveShell.separate_in = ''
nosep_config.InteractiveShell.separate_out = ''
nosep_config.InteractiveShell.separate_out2 = ''

shell_flags['nosep']=(nosep_config, "Eliminate all spacing between prompts.")
shell_flags['pylab'] = (
    {'InteractiveShellApp' : {'pylab' : 'auto'}},
    """Pre-load matplotlib and numpy for interactive use with
    the default matplotlib backend. The exact options available
    depend on what Matplotlib provides at runtime.""",
)
```
