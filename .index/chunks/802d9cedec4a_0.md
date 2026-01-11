# Chunk: 802d9cedec4a_0

- source: `.venv-lab/Lib/site-packages/babel/util.py`
- lines: 1-106
- chunk: 1/4

```
"""
    babel.util
    ~~~~~~~~~~

    Various utility classes and functions.

    :copyright: (c) 2013-2025 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import codecs
import datetime
import os
import re
import textwrap
import warnings
from collections.abc import Generator, Iterable
from typing import IO, Any, TypeVar

from babel import dates, localtime

missing = object()

_T = TypeVar("_T")


def distinct(iterable: Iterable[_T]) -> Generator[_T, None, None]:
    """Yield all items in an iterable collection that are distinct.

    Unlike when using sets for a similar effect, the original ordering of the
    items in the collection is preserved by this function.

    >>> print(list(distinct([1, 2, 1, 3, 4, 4])))
    [1, 2, 3, 4]
    >>> print(list(distinct('foobar')))
    ['f', 'o', 'b', 'a', 'r']

    :param iterable: the iterable collection providing the data
    """
    seen = set()
    for item in iter(iterable):
        if item not in seen:
            yield item
            seen.add(item)


# Regexp to match python magic encoding line
PYTHON_MAGIC_COMMENT_re = re.compile(
    br'[ \t\f]* \# .* coding[=:][ \t]*([-\w.]+)', re.VERBOSE)


def parse_encoding(fp: IO[bytes]) -> str | None:
    """Deduce the encoding of a source file from magic comment.

    It does this in the same way as the `Python interpreter`__

    .. __: https://docs.python.org/3.4/reference/lexical_analysis.html#encoding-declarations

    The ``fp`` argument should be a seekable file object.

    (From Jeff Dairiki)
    """
    pos = fp.tell()
    fp.seek(0)
    try:
        line1 = fp.readline()
        has_bom = line1.startswith(codecs.BOM_UTF8)
        if has_bom:
            line1 = line1[len(codecs.BOM_UTF8):]

        m = PYTHON_MAGIC_COMMENT_re.match(line1)
        if not m:
            try:
                import ast
                ast.parse(line1.decode('latin-1'))
            except (ImportError, SyntaxError, UnicodeEncodeError):
                # Either it's a real syntax error, in which case the source is
                # not valid python source, or line2 is a continuation of line1,
                # in which case we don't want to scan line2 for a magic
                # comment.
                pass
            else:
                line2 = fp.readline()
                m = PYTHON_MAGIC_COMMENT_re.match(line2)

        if has_bom:
            if m:
                magic_comment_encoding = m.group(1).decode('latin-1')
                if magic_comment_encoding != 'utf-8':
                    raise SyntaxError(f"encoding problem: {magic_comment_encoding} with BOM")
            return 'utf-8'
        elif m:
            return m.group(1).decode('latin-1')
        else:
            return None
    finally:
        fp.seek(pos)


PYTHON_FUTURE_IMPORT_re = re.compile(
    r'from\s+__future__\s+import\s+\(*(.+)\)*')


def parse_future_flags(fp: IO[bytes], encoding: str = 'latin-1') -> int:
```
