# Chunk: 3dcd7e4aa8d6_0

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/jaraco/collections/__init__.py`
- lines: 1-112
- chunk: 1/10

```
from __future__ import annotations

import collections.abc
import copy
import functools
import itertools
import operator
import random
import re
from collections.abc import Container, Iterable, Mapping
from typing import TYPE_CHECKING, Any, Callable, Dict, TypeVar, Union, overload

import jaraco.text

if TYPE_CHECKING:
    from _operator import _SupportsComparison

    from _typeshed import SupportsKeysAndGetItem
    from typing_extensions import Self

    _RangeMapKT = TypeVar('_RangeMapKT', bound=_SupportsComparison)
else:
    # _SupportsComparison doesn't exist at runtime,
    # but _RangeMapKT is used in RangeMap's superclass' type parameters
    _RangeMapKT = TypeVar('_RangeMapKT')

_T = TypeVar('_T')
_VT = TypeVar('_VT')

_Matchable = Union[Callable, Container, Iterable, re.Pattern]


def _dispatch(obj: _Matchable) -> Callable:
    # can't rely on singledispatch for Union[Container, Iterable]
    # due to ambiguity
    # (https://peps.python.org/pep-0443/#abstract-base-classes).
    if isinstance(obj, re.Pattern):
        return obj.fullmatch
    # mypy issue: https://github.com/python/mypy/issues/11071
    if not isinstance(obj, Callable):  # type: ignore[arg-type]
        if not isinstance(obj, Container):
            obj = set(obj)  # type: ignore[arg-type]
        obj = obj.__contains__
    return obj  # type: ignore[return-value]


class Projection(collections.abc.Mapping):
    """
    Project a set of keys over a mapping

    >>> sample = {'a': 1, 'b': 2, 'c': 3}
    >>> prj = Projection(['a', 'c', 'd'], sample)
    >>> dict(prj)
    {'a': 1, 'c': 3}

    Projection also accepts an iterable or callable or pattern.

    >>> iter_prj = Projection(iter('acd'), sample)
    >>> call_prj = Projection(lambda k: ord(k) in (97, 99, 100), sample)
    >>> pat_prj = Projection(re.compile(r'[acd]'), sample)
    >>> prj == iter_prj == call_prj == pat_prj
    True

    Keys should only appear if they were specified and exist in the space.
    Order is retained.

    >>> list(prj)
    ['a', 'c']

    Attempting to access a key not in the projection
    results in a KeyError.

    >>> prj['b']
    Traceback (most recent call last):
    ...
    KeyError: 'b'

    Use the projection to update another dict.

    >>> target = {'a': 2, 'b': 2}
    >>> target.update(prj)
    >>> target
    {'a': 1, 'b': 2, 'c': 3}

    Projection keeps a reference to the original dict, so
    modifying the original dict may modify the Projection.

    >>> del sample['a']
    >>> dict(prj)
    {'c': 3}
    """

    def __init__(self, keys: _Matchable, space: Mapping):
        self._match = _dispatch(keys)
        self._space = space

    def __getitem__(self, key):
        if not self._match(key):
            raise KeyError(key)
        return self._space[key]

    def _keys_resolved(self):
        return filter(self._match, self._space)

    def __iter__(self):
        return self._keys_resolved()

    def __len__(self):
        return len(tuple(self._keys_resolved()))
```
