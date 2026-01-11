# Chunk: cebaecbbd1d7_0

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 1-81
- chunk: 1/13

```
"""distutils.command.build_ext

Implements the Distutils 'build_ext' command, for building extension
modules (currently limited to C extensions, should accommodate C++
extensions ASAP)."""

from __future__ import annotations

import contextlib
import os
import re
import sys
from collections.abc import Callable
from distutils._log import log
from site import USER_BASE
from typing import ClassVar

from .._modified import newer_group
from ..ccompiler import new_compiler, show_compilers
from ..core import Command
from ..errors import (
    CCompilerError,
    CompileError,
    DistutilsError,
    DistutilsOptionError,
    DistutilsPlatformError,
    DistutilsSetupError,
)
from ..extension import Extension
from ..sysconfig import customize_compiler, get_config_h_filename, get_python_version
from ..util import get_platform, is_freethreaded, is_mingw

# An extension name is just a dot-separated list of Python NAMEs (ie.
# the same as a fully-qualified module name).
extension_name_re = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*$')


class build_ext(Command):
    description = "build C/C++ extensions (compile/link to build directory)"

    # XXX thoughts on how to deal with complex command-line options like
    # these, i.e. how to make it so fancy_getopt can suck them off the
    # command line and make it look like setup.py defined the appropriate
    # lists of tuples of what-have-you.
    #   - each command needs a callback to process its command-line options
    #   - Command.__init__() needs access to its share of the whole
    #     command line (must ultimately come from
    #     Distribution.parse_command_line())
    #   - it then calls the current command class' option-parsing
    #     callback to deal with weird options like -D, which have to
    #     parse the option text and churn out some custom data
    #     structure
    #   - that data structure (in this case, a list of 2-tuples)
    #     will then be present in the command object by the time
    #     we get to finalize_options() (i.e. the constructor
    #     takes care of both command-line and client options
    #     in between initialize_options() and finalize_options())

    sep_by = f" (separated by '{os.pathsep}')"
    user_options = [
        ('build-lib=', 'b', "directory for compiled extension modules"),
        ('build-temp=', 't', "directory for temporary files (build by-products)"),
        (
            'plat-name=',
            'p',
            "platform name to cross-compile for, if supported "
            f"[default: {get_platform()}]",
        ),
        (
            'inplace',
            'i',
            "ignore build-lib and put compiled extensions into the source "
            "directory alongside your pure Python modules",
        ),
        (
            'include-dirs=',
            'I',
            "list of directories to search for header files" + sep_by,
        ),
        ('define=', 'D', "C preprocessor macros to define"),
```
