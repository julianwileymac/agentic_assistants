# Chunk: 759f5aece4ff_0

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 1-117
- chunk: 1/9

```
from __future__ import annotations

import builtins
import importlib
import os.path
import platform
import shutil
import stat
import struct
import sys
import sysconfig
from contextlib import suppress
from inspect import cleandoc
from zipfile import ZipFile

import jaraco.path
import pytest
from packaging import tags

import setuptools
from setuptools.command.bdist_wheel import bdist_wheel, get_abi_tag
from setuptools.dist import Distribution
from setuptools.warnings import SetuptoolsDeprecationWarning

from distutils.core import run_setup

DEFAULT_FILES = {
    "dummy_dist-1.0.dist-info/top_level.txt",
    "dummy_dist-1.0.dist-info/METADATA",
    "dummy_dist-1.0.dist-info/WHEEL",
    "dummy_dist-1.0.dist-info/RECORD",
}
DEFAULT_LICENSE_FILES = {
    "LICENSE",
    "LICENSE.txt",
    "LICENCE",
    "LICENCE.txt",
    "COPYING",
    "COPYING.md",
    "NOTICE",
    "NOTICE.rst",
    "AUTHORS",
    "AUTHORS.txt",
}
OTHER_IGNORED_FILES = {
    "LICENSE~",
    "AUTHORS~",
}
SETUPPY_EXAMPLE = """\
from setuptools import setup

setup(
    name='dummy_dist',
    version='1.0',
)
"""


EXAMPLES = {
    "dummy-dist": {
        "setup.py": SETUPPY_EXAMPLE,
        "licenses_dir": {"DUMMYFILE": ""},
        **dict.fromkeys(DEFAULT_LICENSE_FILES | OTHER_IGNORED_FILES, ""),
    },
    "simple-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="simple.dist",
                version="0.1",
                description="A testing distribution \N{SNOWMAN}",
                extras_require={"voting": ["beaglevote"]},
            )
            """
        ),
        "simpledist": "",
    },
    "complex-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="complex-dist",
                version="0.1",
                description="Another testing distribution \N{SNOWMAN}",
                long_description="Another testing distribution \N{SNOWMAN}",
                author="Illustrious Author",
                author_email="illustrious@example.org",
                url="http://example.org/exemplary",
                packages=["complexdist"],
                setup_requires=["setuptools"],
                install_requires=["quux", "splort"],
                extras_require={"simple": ["simple.dist"]},
                entry_points={
                    "console_scripts": [
                        "complex-dist=complexdist:main",
                        "complex-dist2=complexdist:main",
                    ],
                },
            )
            """
        ),
        "complexdist": {"__init__.py": "def main(): return"},
    },
    "headers-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="headers.dist",
                version="0.1",
                description="A distribution with headers",
```
