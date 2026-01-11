# Chunk: 72cb71dffcc7_1

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 77-172
- chunk: 2/18

```
om collections.abc import Sequence
from types import TracebackType
from typing import Any, List, Optional, Tuple
from collections.abc import Callable

import stack_data
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.token import Token

from IPython import get_ipython
from IPython.utils import path as util_path
from IPython.utils import py3compat
from IPython.utils.PyColorize import Parser, Theme, TokenStream, theme_table
from IPython.utils.terminal import get_terminal_size

from .display_trap import DisplayTrap
from .doctb import DocTB
from .tbtools import (
    FrameInfo,
    TBTools,
    _format_traceback_lines,
    _safe_string,
    _simple_format_traceback_lines,
    _tokens_filename,
    eqrepr,
    get_line_number_of_frame,
    nullrepr,
    text_repr,
)

# Globals
# amount of space to put line numbers before verbose tracebacks
INDENT_SIZE = 8

# When files are too long do not use stackdata to get frames.
# it is too long.
FAST_THRESHOLD = 10_000

# ---------------------------------------------------------------------------
class ListTB(TBTools):
    """Print traceback information from a traceback list, with optional color.

    Calling requires 3 arguments: (etype, evalue, elist)
    as would be obtained by::

      etype, evalue, tb = sys.exc_info()
      if tb:
        elist = traceback.extract_tb(tb)
      else:
        elist = None

    It can thus be used by programs which need to process the traceback before
    printing (such as console replacements based on the code module from the
    standard library).

    Because they are meant to be called without a full traceback (only a
    list), instances of this class can't call the interactive pdb debugger."""

    def __call__(
        self,
        etype: type[BaseException],
        evalue: BaseException | None,
        etb: TracebackType | None,
    ) -> None:
        self.ostream.flush()
        self.ostream.write(self.text(etype, evalue, etb))
        self.ostream.write("\n")

    def _extract_tb(self, tb: TracebackType | None) -> traceback.StackSummary | None:
        if tb:
            return traceback.extract_tb(tb)
        else:
            return None

    def structured_traceback(
        self,
        etype: type,
        evalue: Optional[BaseException],
        etb: Optional[TracebackType] = None,
        tb_offset: Optional[int] = None,
        context: int = 5,
    ) -> list[str]:
        """Return a color formatted string with the traceback info.

        Parameters
        ----------
        etype : exception type
            Type of the exception raised.
        evalue : object
            Data stored in the exception
        etb : list | TracebackType | None
            If list: List of frames, see class docstring for details.
            If Traceback: Traceback of the exception.
        tb_offset : int, optional
            Number of frames in the traceback to skip.  If not given, the
```
