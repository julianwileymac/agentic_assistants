# Chunk: cd1508bbafba_0

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 1-105
- chunk: 1/7

```
"""
Module to define and register Terminal IPython shortcuts with
:mod:`prompt_toolkit`
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import signal
import sys
import warnings
from dataclasses import dataclass
from typing import Any, Optional, List
from collections.abc import Callable

from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.key_binding.bindings import named_commands as nc
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.vi_state import InputMode, ViState
from prompt_toolkit.filters import Condition

from IPython.core.getipython import get_ipython
from . import auto_match as match
from . import auto_suggest
from .filters import filter_from_string
from IPython.utils.decorators import undoc

from prompt_toolkit.enums import DEFAULT_BUFFER

__all__ = ["create_ipython_shortcuts"]


@dataclass
class BaseBinding:
    command: Callable[[KeyPressEvent], Any]
    keys: List[str]


@dataclass
class RuntimeBinding(BaseBinding):
    filter: Condition


@dataclass
class Binding(BaseBinding):
    # while filter could be created by referencing variables directly (rather
    # than created from strings), by using strings we ensure that users will
    # be able to create filters in configuration (e.g. JSON) files too, which
    # also benefits the documentation by enforcing human-readable filter names.
    condition: Optional[str] = None

    def __post_init__(self):
        if self.condition:
            self.filter = filter_from_string(self.condition)
        else:
            self.filter = None


def create_identifier(handler: Callable):
    parts = handler.__module__.split(".")
    name = handler.__name__
    package = parts[0]
    if len(parts) > 1:
        final_module = parts[-1]
        return f"{package}:{final_module}.{name}"
    else:
        return f"{package}:{name}"


AUTO_MATCH_BINDINGS = [
    *[
        Binding(
            cmd, [key], "focused_insert & auto_match & followed_by_closing_paren_or_end"
        )
        for key, cmd in match.auto_match_parens.items()
    ],
    *[
        # raw string
        Binding(cmd, [key], "focused_insert & auto_match & preceded_by_raw_str_prefix")
        for key, cmd in match.auto_match_parens_raw_string.items()
    ],
    Binding(
        match.double_quote,
        ['"'],
        "focused_insert"
        " & auto_match"
        " & not_inside_unclosed_string"
        " & preceded_by_paired_double_quotes"
        " & followed_by_closing_paren_or_end",
    ),
    Binding(
        match.single_quote,
        ["'"],
        "focused_insert"
        " & auto_match"
        " & not_inside_unclosed_string"
        " & preceded_by_paired_single_quotes"
        " & followed_by_closing_paren_or_end",
    ),
```
