# Chunk: 6adf7c8aec72_0

- source: `.venv-lab/Lib/site-packages/bs4/diagnose.py`
- lines: 1-102
- chunk: 1/3

```
"""Diagnostic functions, mainly for use when doing tech support."""

# Use of this source code is governed by the MIT license.
__license__ = "MIT"

import cProfile
from io import BytesIO
from html.parser import HTMLParser
import bs4
from bs4 import BeautifulSoup, __version__
from bs4.builder import builder_registry
from typing import (
    Any,
    IO,
    List,
    Optional,
    Tuple,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from bs4._typing import _IncomingMarkup

import pstats
import random
import tempfile
import time
import traceback
import sys


def diagnose(data: "_IncomingMarkup") -> None:
    """Diagnostic suite for isolating common problems.

    :param data: Some markup that needs to be explained.
    :return: None; diagnostics are printed to standard output.
    """
    print(("Diagnostic running on Beautiful Soup %s" % __version__))
    print(("Python version %s" % sys.version))

    basic_parsers = ["html.parser", "html5lib", "lxml"]
    for name in basic_parsers:
        for builder in builder_registry.builders:
            if name in builder.features:
                break
        else:
            basic_parsers.remove(name)
            print(
                ("I noticed that %s is not installed. Installing it may help." % name)
            )

    if "lxml" in basic_parsers:
        basic_parsers.append("lxml-xml")
        try:
            from lxml import etree # type:ignore

            print(("Found lxml version %s" % ".".join(map(str, etree.LXML_VERSION))))
        except ImportError:
            print("lxml is not installed or couldn't be imported.")

    if "html5lib" in basic_parsers:
        try:
            import html5lib

            print(("Found html5lib version %s" % html5lib.__version__))
        except ImportError:
            print("html5lib is not installed or couldn't be imported.")

    if hasattr(data, "read"):
        data = data.read()

    for parser in basic_parsers:
        print(("Trying to parse your markup with %s" % parser))
        success = False
        try:
            soup = BeautifulSoup(data, features=parser)
            success = True
        except Exception:
            print(("%s could not parse the markup." % parser))
            traceback.print_exc()
        if success:
            print(("Here's what %s did with the markup:" % parser))
            print((soup.prettify()))

        print(("-" * 80))


def lxml_trace(data: "_IncomingMarkup", html: bool = True, **kwargs: Any) -> None:
    """Print out the lxml events that occur during parsing.

    This lets you see how lxml parses a document when no Beautiful
    Soup code is running. You can use this to determine whether
    an lxml-specific problem is in Beautiful Soup's lxml tree builders
    or in lxml itself.

    :param data: Some markup.
    :param html: If True, markup will be parsed with lxml's HTML parser.
       if False, lxml's XML parser will be used.
    """
    from lxml import etree
```
