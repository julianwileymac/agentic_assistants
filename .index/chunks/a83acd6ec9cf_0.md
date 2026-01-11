# Chunk: a83acd6ec9cf_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/input/vt100_parser.py`
- lines: 1-104
- chunk: 1/4

```
"""
Parser for VT100 input stream.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, Generator

from ..key_binding.key_processor import KeyPress
from ..keys import Keys
from .ansi_escape_sequences import ANSI_SEQUENCES

__all__ = [
    "Vt100Parser",
]


# Regex matching any CPR response
# (Note that we use '\Z' instead of '$', because '$' could include a trailing
# newline.)
_cpr_response_re = re.compile("^" + re.escape("\x1b[") + r"\d+;\d+R\Z")

# Mouse events:
# Typical: "Esc[MaB*"  Urxvt: "Esc[96;14;13M" and for Xterm SGR: "Esc[<64;85;12M"
_mouse_event_re = re.compile("^" + re.escape("\x1b[") + r"(<?[\d;]+[mM]|M...)\Z")

# Regex matching any valid prefix of a CPR response.
# (Note that it doesn't contain the last character, the 'R'. The prefix has to
# be shorter.)
_cpr_response_prefix_re = re.compile("^" + re.escape("\x1b[") + r"[\d;]*\Z")

_mouse_event_prefix_re = re.compile("^" + re.escape("\x1b[") + r"(<?[\d;]*|M.{0,2})\Z")


class _Flush:
    """Helper object to indicate flush operation to the parser."""

    pass


class _IsPrefixOfLongerMatchCache(Dict[str, bool]):
    """
    Dictionary that maps input sequences to a boolean indicating whether there is
    any key that start with this characters.
    """

    def __missing__(self, prefix: str) -> bool:
        # (hard coded) If this could be a prefix of a CPR response, return
        # True.
        if _cpr_response_prefix_re.match(prefix) or _mouse_event_prefix_re.match(
            prefix
        ):
            result = True
        else:
            # If this could be a prefix of anything else, also return True.
            result = any(
                v
                for k, v in ANSI_SEQUENCES.items()
                if k.startswith(prefix) and k != prefix
            )

        self[prefix] = result
        return result


_IS_PREFIX_OF_LONGER_MATCH_CACHE = _IsPrefixOfLongerMatchCache()


class Vt100Parser:
    """
    Parser for VT100 input stream.
    Data can be fed through the `feed` method and the given callback will be
    called with KeyPress objects.

    ::

        def callback(key):
            pass
        i = Vt100Parser(callback)
        i.feed('data\x01...')

    :attr feed_key_callback: Function that will be called when a key is parsed.
    """

    # Lookup table of ANSI escape sequences for a VT100 terminal
    # Hint: in order to know what sequences your terminal writes to stdin, run
    #       "od -c" and start typing.
    def __init__(self, feed_key_callback: Callable[[KeyPress], None]) -> None:
        self.feed_key_callback = feed_key_callback
        self.reset()

    def reset(self, request: bool = False) -> None:
        self._in_bracketed_paste = False
        self._start_parser()

    def _start_parser(self) -> None:
        """
        Start the parser coroutine.
        """
        self._input_parser = self._input_parser_generator()
        self._input_parser.send(None)  # type: ignore
```
