# Chunk: bcc3c6bec4b8_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/distlib/util.py`
- lines: 1-94
- chunk: 1/25

```
#
# Copyright (C) 2012-2023 The Python Software Foundation.
# See LICENSE.txt and CONTRIBUTORS.txt.
#
import codecs
from collections import deque
import contextlib
import csv
from glob import iglob as std_iglob
import io
import json
import logging
import os
import py_compile
import re
import socket
try:
    import ssl
except ImportError:  # pragma: no cover
    ssl = None
import subprocess
import sys
import tarfile
import tempfile
import textwrap

try:
    import threading
except ImportError:  # pragma: no cover
    import dummy_threading as threading
import time

from . import DistlibException
from .compat import (string_types, text_type, shutil, raw_input, StringIO, cache_from_source, urlopen, urljoin, httplib,
                     xmlrpclib, HTTPHandler, BaseConfigurator, valid_ident, Container, configparser, URLError, ZipFile,
                     fsdecode, unquote, urlparse)

logger = logging.getLogger(__name__)

#
# Requirement parsing code as per PEP 508
#

IDENTIFIER = re.compile(r'^([\w\.-]+)\s*')
VERSION_IDENTIFIER = re.compile(r'^([\w\.*+-]+)\s*')
COMPARE_OP = re.compile(r'^(<=?|>=?|={2,3}|[~!]=)\s*')
MARKER_OP = re.compile(r'^((<=?)|(>=?)|={2,3}|[~!]=|in|not\s+in)\s*')
OR = re.compile(r'^or\b\s*')
AND = re.compile(r'^and\b\s*')
NON_SPACE = re.compile(r'(\S+)\s*')
STRING_CHUNK = re.compile(r'([\s\w\.{}()*+#:;,/?!~`@$%^&=|<>\[\]-]+)')


def parse_marker(marker_string):
    """
    Parse a marker string and return a dictionary containing a marker expression.

    The dictionary will contain keys "op", "lhs" and "rhs" for non-terminals in
    the expression grammar, or strings. A string contained in quotes is to be
    interpreted as a literal string, and a string not contained in quotes is a
    variable (such as os_name).
    """

    def marker_var(remaining):
        # either identifier, or literal string
        m = IDENTIFIER.match(remaining)
        if m:
            result = m.groups()[0]
            remaining = remaining[m.end():]
        elif not remaining:
            raise SyntaxError('unexpected end of input')
        else:
            q = remaining[0]
            if q not in '\'"':
                raise SyntaxError('invalid expression: %s' % remaining)
            oq = '\'"'.replace(q, '')
            remaining = remaining[1:]
            parts = [q]
            while remaining:
                # either a string chunk, or oq, or q to terminate
                if remaining[0] == q:
                    break
                elif remaining[0] == oq:
                    parts.append(oq)
                    remaining = remaining[1:]
                else:
                    m = STRING_CHUNK.match(remaining)
                    if not m:
                        raise SyntaxError('error in string literal: %s' % remaining)
                    parts.append(m.groups()[0])
                    remaining = remaining[m.end():]
            else:
                s = ''.join(parts)
```
