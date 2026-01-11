# Chunk: dacf7e9b9f9b_0

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/install_lib.py`
- lines: 1-84
- chunk: 1/4

```
"""distutils.command.install_lib

Implements the Distutils 'install_lib' command
(install all Python modules)."""

from __future__ import annotations

import importlib.util
import os
import sys
from typing import Any, ClassVar

from ..core import Command
from ..errors import DistutilsOptionError

# Extension for Python source files.
PYTHON_SOURCE_EXTENSION = ".py"


class install_lib(Command):
    description = "install all Python modules (extensions and pure Python)"

    # The byte-compilation options are a tad confusing.  Here are the
    # possible scenarios:
    #   1) no compilation at all (--no-compile --no-optimize)
    #   2) compile .pyc only (--compile --no-optimize; default)
    #   3) compile .pyc and "opt-1" .pyc (--compile --optimize)
    #   4) compile "opt-1" .pyc only (--no-compile --optimize)
    #   5) compile .pyc and "opt-2" .pyc (--compile --optimize-more)
    #   6) compile "opt-2" .pyc only (--no-compile --optimize-more)
    #
    # The UI for this is two options, 'compile' and 'optimize'.
    # 'compile' is strictly boolean, and only decides whether to
    # generate .pyc files.  'optimize' is three-way (0, 1, or 2), and
    # decides both whether to generate .pyc files and what level of
    # optimization to use.

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('build-dir=', 'b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', None, "don't compile .py files"),
        (
            'optimize=',
            'O',
            "also compile with optimization: -O1 for \"python -O\", "
            "-O2 for \"python -OO\", and -O0 to disable [default: -O0]",
        ),
        ('skip-build', None, "skip the build steps"),
    ]

    boolean_options: ClassVar[list[str]] = ['force', 'compile', 'skip-build']
    negative_opt: ClassVar[dict[str, str]] = {'no-compile': 'compile'}

    def initialize_options(self):
        # let the 'install' command dictate our installation directory
        self.install_dir = None
        self.build_dir = None
        self.force = False
        self.compile = None
        self.optimize = None
        self.skip_build = None

    def finalize_options(self) -> None:
        # Get all the information we need to install pure Python modules
        # from the umbrella 'install' command -- build (source) directory,
        # install (target) directory, and whether to compile .py files.
        self.set_undefined_options(
            'install',
            ('build_lib', 'build_dir'),
            ('install_lib', 'install_dir'),
            ('force', 'force'),
            ('compile', 'compile'),
            ('optimize', 'optimize'),
            ('skip_build', 'skip_build'),
        )

        if self.compile is None:
            self.compile = True
        if self.optimize is None:
            self.optimize = False
```
