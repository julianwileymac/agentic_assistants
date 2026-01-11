# Chunk: 6bf0f0cc36da_1

- source: `.venv-lab/Lib/site-packages/tornado/options.py`
- lines: 70-164
- chunk: 2/10

```


`tornado.options.options` is a singleton instance of `OptionParser`, and
the top-level functions in this module (`define`, `parse_command_line`, etc)
simply call methods on it.  You may create additional `OptionParser`
instances to define isolated sets of options, such as for subcommands.

.. note::

   By default, several options are defined that will configure the
   standard `logging` module when `parse_command_line` or `parse_config_file`
   are called.  If you want Tornado to leave the logging configuration
   alone so you can manage it yourself, either pass ``--logging=none``
   on the command line or do the following to disable it in code::

       from tornado.options import options, parse_command_line
       options.logging = None
       parse_command_line()

.. note::

   `parse_command_line` or `parse_config_file` function should called after
   logging configuration and user-defined command line flags using the
   ``callback`` option definition, or these configurations will not take effect.

.. versionchanged:: 4.3
   Dashes and underscores are fully interchangeable in option names;
   options can be defined, set, and read with any mix of the two.
   Dashes are typical for command-line usage while config files require
   underscores.
"""

import datetime
import numbers
import re
import sys
import os
import textwrap

from tornado.escape import _unicode, native_str
from tornado.log import define_logging_options
from tornado.util import basestring_type, exec_in

from typing import (
    Any,
    Iterator,
    Iterable,
    Tuple,
    Set,
    Dict,
    Callable,
    List,
    TextIO,
    Optional,
)


class Error(Exception):
    """Exception raised by errors in the options module."""

    pass


class OptionParser:
    """A collection of options, a dictionary with object-like access.

    Normally accessed via static functions in the `tornado.options` module,
    which reference a global instance.
    """

    def __init__(self) -> None:
        # we have to use self.__dict__ because we override setattr.
        self.__dict__["_options"] = {}
        self.__dict__["_parse_callbacks"] = []
        self.define(
            "help",
            type=bool,
            help="show this help information",
            callback=self._help_callback,
        )

    def _normalize_name(self, name: str) -> str:
        return name.replace("_", "-")

    def __getattr__(self, name: str) -> Any:
        name = self._normalize_name(name)
        if isinstance(self._options.get(name), _Option):
            return self._options[name].value()
        raise AttributeError("Unrecognized option %r" % name)

    def __setattr__(self, name: str, value: Any) -> None:
        name = self._normalize_name(name)
        if isinstance(self._options.get(name), _Option):
            return self._options[name].set(value)
```
