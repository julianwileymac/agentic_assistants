# Chunk: 5eaf55f2bd3f_0

- source: `.venv-lab/Lib/site-packages/IPython/core/doctb.py`
- lines: 1-115
- chunk: 1/6

```
import inspect
import linecache
import sys
from collections.abc import Sequence
from types import TracebackType
from typing import Any, Optional
from collections.abc import Callable

import stack_data
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.token import Token

from IPython.utils.PyColorize import Theme, TokenStream, theme_table
from IPython.utils.terminal import get_terminal_size

from .tbtools import (
    FrameInfo,
    TBTools,
    _safe_string,
    _tokens_filename,
    eqrepr,
    get_line_number_of_frame,
    nullrepr,
)

INDENT_SIZE = 8


def _format_traceback_lines(
    lines: list[stack_data.Line],
    theme: Theme,
    has_colors: bool,
    lvals_toks: list[TokenStream],
) -> TokenStream:
    """
    Format tracebacks lines with pointing arrow, leading numbers,
    this assumes the stack have been extracted using stackdata.


    Parameters
    ----------
    lines : list[Line]
    """
    numbers_width = INDENT_SIZE - 1
    tokens: TokenStream = [(Token, "\n")]

    for stack_line in lines:
        if stack_line is stack_data.LINE_GAP:
            toks = [(Token.LinenoEm, "   (...)")]
            tokens.extend(toks)
            continue

        lineno = stack_line.lineno
        line = stack_line.render(pygmented=has_colors).rstrip("\n") + "\n"
        if stack_line.is_current:
            # This is the line with the error
            pad = numbers_width - len(str(lineno))
            toks = [
                (Token.Prompt, theme.make_arrow(3)),
                (Token, " "),
                (Token, line),
            ]
        else:
            # num = "%*s" % (numbers_width, lineno)
            toks = [
                # (Token.LinenoEm, str(num)),
                (Token, "..."),
                (Token, " "),
                (Token, line),
            ]

        tokens.extend(toks)
        if lvals_toks and stack_line.is_current:
            for lv in lvals_toks:
                tokens.append((Token, " " * INDENT_SIZE))
                tokens.extend(lv)
                tokens.append((Token, "\n"))
            # strip the last newline
            tokens = tokens[:-1]

    return tokens


class DocTB(TBTools):
    """

    A stripped down version of Verbose TB, simplified to not have too much information when
    running doctests

    """

    tb_highlight = ""
    tb_highlight_style = "default"
    tb_offset: int
    long_header: bool
    include_vars: bool

    _mode: str

    def __init__(
        self,
        # TODO: no default ?
        theme_name: str = "linux",
        call_pdb: bool = False,
        ostream: Any = None,
        tb_offset: int = 0,
        long_header: bool = False,
        include_vars: bool = True,
        check_cache: Callable[[], None] | None = None,
        debugger_cls: type | None = None,
    ):
        """Specify traceback offset, headers and color scheme.

        Define how many frames to drop from the tracebacks. Calling it with
```
