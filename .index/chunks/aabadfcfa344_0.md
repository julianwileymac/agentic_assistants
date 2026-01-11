# Chunk: aabadfcfa344_0

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/config.py`
- lines: 1-88
- chunk: 1/5

```
"""distutils.command.config

Implements the Distutils 'config' command, a (mostly) empty command class
that exists mainly to be sub-classed by specific module distributions and
applications.  The idea is that while every "config" command is different,
at least they're all named the same, and users always see "config" in the
list of standard commands.  Also, this is a good place to put common
configure-like tasks: "try to compile this C code", or "figure out where
this header file lives".
"""

from __future__ import annotations

import os
import pathlib
import re
from collections.abc import Sequence
from distutils._log import log

from ..ccompiler import CCompiler, CompileError, LinkError, new_compiler
from ..core import Command
from ..errors import DistutilsExecError
from ..sysconfig import customize_compiler

LANG_EXT = {"c": ".c", "c++": ".cxx"}


class config(Command):
    description = "prepare to build"

    user_options = [
        ('compiler=', None, "specify the compiler type"),
        ('cc=', None, "specify the compiler executable"),
        ('include-dirs=', 'I', "list of directories to search for header files"),
        ('define=', 'D', "C preprocessor macros to define"),
        ('undef=', 'U', "C preprocessor macros to undefine"),
        ('libraries=', 'l', "external C libraries to link with"),
        ('library-dirs=', 'L', "directories to search for external C libraries"),
        ('noisy', None, "show every action (compile, link, run, ...) taken"),
        (
            'dump-source',
            None,
            "dump generated source files before attempting to compile them",
        ),
    ]

    # The three standard command methods: since the "config" command
    # does nothing by default, these are empty.

    def initialize_options(self):
        self.compiler = None
        self.cc = None
        self.include_dirs = None
        self.libraries = None
        self.library_dirs = None

        # maximal output for now
        self.noisy = 1
        self.dump_source = 1

        # list of temporary files generated along-the-way that we have
        # to clean at some point
        self.temp_files = []

    def finalize_options(self):
        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        elif isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        if self.libraries is None:
            self.libraries = []
        elif isinstance(self.libraries, str):
            self.libraries = [self.libraries]

        if self.library_dirs is None:
            self.library_dirs = []
        elif isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

    def run(self):
        pass

    # Utility methods for actual "config" commands.  The interfaces are
    # loosely based on Autoconf macros of similar names.  Sub-classes
    # may use these freely.
```
