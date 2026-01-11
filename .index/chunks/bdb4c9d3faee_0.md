# Chunk: bdb4c9d3faee_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pkg_resources/__init__.py`
- lines: 1-115
- chunk: 1/47

```
# TODO: Add Generic type annotations to initialized collections.
# For now we'd simply use implicit Any/Unknown which would add redundant annotations
# mypy: disable-error-code="var-annotated"
"""
Package resource API
--------------------

A resource is a logical file contained within a package, or a logical
subdirectory thereof.  The package resource API expects resource names
to have their path parts separated with ``/``, *not* whatever the local
path separator is.  Do not use os.path operations to manipulate resource
names being passed into the API.

The package resource API is designed to work with normal filesystem packages,
.egg files, and unpacked .egg files.  It can also work in a limited way with
.zip files and with custom PEP 302 loaders that support the ``get_data()``
method.

This module is deprecated. Users are directed to :mod:`importlib.resources`,
:mod:`importlib.metadata` and :pypi:`packaging` instead.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 8):  # noqa: UP036 # Check for unsupported versions
    raise RuntimeError("Python 3.8 or later is required")

import os
import io
import time
import re
import types
from typing import (
    Any,
    Literal,
    Dict,
    Iterator,
    Mapping,
    MutableSequence,
    NamedTuple,
    NoReturn,
    Tuple,
    Union,
    TYPE_CHECKING,
    Protocol,
    Callable,
    Iterable,
    TypeVar,
    overload,
)
import zipfile
import zipimport
import warnings
import stat
import functools
import pkgutil
import operator
import platform
import collections
import plistlib
import email.parser
import errno
import tempfile
import textwrap
import inspect
import ntpath
import posixpath
import importlib
import importlib.abc
import importlib.machinery
from pkgutil import get_importer

import _imp

# capture these to bypass sandboxing
from os import utime
from os import open as os_open
from os.path import isdir, split

try:
    from os import mkdir, rename, unlink

    WRITE_SUPPORT = True
except ImportError:
    # no write support, probably under GAE
    WRITE_SUPPORT = False

from pip._internal.utils._jaraco_text import (
    yield_lines,
    drop_comment,
    join_continuation,
)
from pip._vendor.packaging import markers as _packaging_markers
from pip._vendor.packaging import requirements as _packaging_requirements
from pip._vendor.packaging import utils as _packaging_utils
from pip._vendor.packaging import version as _packaging_version
from pip._vendor.platformdirs import user_cache_dir as _user_cache_dir

if TYPE_CHECKING:
    from _typeshed import BytesPath, StrPath, StrOrBytesPath
    from typing_extensions import Self


# Patch: Remove deprecation warning from vendored pkg_resources.
# Setting PYTHONWARNINGS=error to verify builds produce no warnings
# causes immediate exceptions.
# See https://github.com/pypa/pip/issues/12243


_T = TypeVar("_T")
_DistributionT = TypeVar("_DistributionT", bound="Distribution")
# Type aliases
```
