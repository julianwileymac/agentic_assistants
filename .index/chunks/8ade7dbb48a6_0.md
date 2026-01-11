# Chunk: 8ade7dbb48a6_0

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 1-96
- chunk: 1/11

```
from __future__ import annotations

"""Magic functions for InteractiveShell."""

# -----------------------------------------------------------------------------
#  Copyright (C) 2001 Janko Hauser <jhauser@zscout.de> and
#  Copyright (C) 2001 Fernando Perez <fperez@colorado.edu>
#  Copyright (C) 2008 The IPython Development Team

#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------

import os
import re
import sys
from getopt import getopt, GetoptError

from traitlets.config.configurable import Configurable
from . import oinspect
from .error import UsageError
from .inputtransformer2 import ESC_MAGIC, ESC_MAGIC2
from ..utils.ipstruct import Struct
from ..utils.process import arg_split
from ..utils.text import dedent
from traitlets import Bool, Dict, Instance, observe
from logging import error

import typing as t

if t.TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

# A dict we'll use for each class that has magics, used as temporary storage to
# pass information between the @line/cell_magic method decorators and the
# @magics_class class decorator, because the method decorators have no
# access to the class when they run.  See for more details:
# http://stackoverflow.com/questions/2366713/can-a-python-decorator-of-an-instance-method-access-the-class

magics: t.Dict = dict(line={}, cell={})

magic_kinds = ("line", "cell")
magic_spec = ("line", "cell", "line_cell")
magic_escapes = dict(line=ESC_MAGIC, cell=ESC_MAGIC2)

# -----------------------------------------------------------------------------
# Utility classes and functions
# -----------------------------------------------------------------------------


class Bunch:
    pass


def on_off(tag):
    """Return an ON/OFF string for a 1/0 input. Simple utility function."""
    return ["OFF", "ON"][tag]


def compress_dhist(dh):
    """Compress a directory history into a new one with at most 20 entries.

    Return a new list made from the first and last 10 elements of dhist after
    removal of duplicates.
    """
    head, tail = dh[:-10], dh[-10:]

    newhead = []
    done = set()
    for h in head:
        if h in done:
            continue
        newhead.append(h)
        done.add(h)

    return newhead + tail


def needs_local_scope(func):
    """Decorator to mark magic functions which need to local scope to run."""
    func.needs_local_scope = True
    return func


# -----------------------------------------------------------------------------
# Class and method decorators for registering magics
# -----------------------------------------------------------------------------


def magics_class(cls):
```
