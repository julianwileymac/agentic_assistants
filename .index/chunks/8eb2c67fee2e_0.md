# Chunk: 8eb2c67fee2e_0

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 1-97
- chunk: 1/17

```
from __future__ import annotations

import functools
import io
import itertools
import numbers
import os
import re
import sys
from collections.abc import Iterable, Iterator, MutableMapping, Sequence
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from more_itertools import partition, unique_everseen
from packaging.markers import InvalidMarker, Marker
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from . import (
    _entry_points,
    _reqs,
    _static,
    command as _,  # noqa: F401 # imported for side-effects
)
from ._importlib import metadata
from ._normalization import _canonicalize_license_expression
from ._path import StrPath
from ._reqs import _StrOrIter
from .config import pyprojecttoml, setupcfg
from .discovery import ConfigDiscovery
from .errors import InvalidConfigError
from .monkey import get_unpatched
from .warnings import InformationOnly, SetuptoolsDeprecationWarning

import distutils.cmd
import distutils.command
import distutils.core
import distutils.dist
import distutils.log
from distutils.debug import DEBUG
from distutils.errors import DistutilsOptionError, DistutilsSetupError
from distutils.fancy_getopt import translate_longopt
from distutils.util import strtobool

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


__all__ = ['Distribution']

_sequence = tuple, list
"""
:meta private:

Supported iterable types that are known to be:
- ordered (which `set` isn't)
- not match a str (which `Sequence[str]` does)
- not imply a nested type (like `dict`)
for use with `isinstance`.
"""
_Sequence: TypeAlias = Union[tuple[str, ...], list[str]]
# This is how stringifying _Sequence would look in Python 3.10
_sequence_type_repr = "tuple[str, ...] | list[str]"
_OrderedStrSequence: TypeAlias = Union[str, dict[str, Any], Sequence[str]]
"""
:meta private:
Avoid single-use iterable. Disallow sets.
A poor approximation of an OrderedSequence (dict doesn't match a Sequence).
"""


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "sequence":
        SetuptoolsDeprecationWarning.emit(
            "`setuptools.dist.sequence` is an internal implementation detail.",
            "Please define your own `sequence = tuple, list` instead.",
            due_date=(2025, 8, 28),  # Originally added on 2024-08-27
        )
        return _sequence
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def check_importable(dist, attr, value):
    try:
        ep = metadata.EntryPoint(value=value, name=None, group=None)
        assert not ep.extras
    except (TypeError, ValueError, AttributeError, AssertionError) as e:
        raise DistutilsSetupError(
            f"{attr!r} must be importable 'module:attrs' string (got {value!r})"
        ) from e


def assert_string_list(dist, attr: str, value: _Sequence) -> None:
    """Verify that value is a string list"""
    try:
```
