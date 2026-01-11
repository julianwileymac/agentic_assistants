# Chunk: 6bfbecc32bf4_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 1-115
- chunk: 1/9

```
"""
Output for vt100 terminals.

A lot of thanks, regarding outputting of colors, goes to the Pygments project:
(We don't rely on Pygments anymore, because many things are very custom, and
everything has been highly optimized.)
http://pygments.org/
"""

from __future__ import annotations

import io
import os
import sys
from typing import Callable, Dict, Hashable, Iterable, Sequence, TextIO, Tuple

from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.data_structures import Size
from prompt_toolkit.output import Output
from prompt_toolkit.styles import ANSI_COLOR_NAMES, Attrs
from prompt_toolkit.utils import is_dumb_terminal

from .color_depth import ColorDepth
from .flush_stdout import flush_stdout

__all__ = [
    "Vt100_Output",
]


FG_ANSI_COLORS = {
    "ansidefault": 39,
    # Low intensity.
    "ansiblack": 30,
    "ansired": 31,
    "ansigreen": 32,
    "ansiyellow": 33,
    "ansiblue": 34,
    "ansimagenta": 35,
    "ansicyan": 36,
    "ansigray": 37,
    # High intensity.
    "ansibrightblack": 90,
    "ansibrightred": 91,
    "ansibrightgreen": 92,
    "ansibrightyellow": 93,
    "ansibrightblue": 94,
    "ansibrightmagenta": 95,
    "ansibrightcyan": 96,
    "ansiwhite": 97,
}

BG_ANSI_COLORS = {
    "ansidefault": 49,
    # Low intensity.
    "ansiblack": 40,
    "ansired": 41,
    "ansigreen": 42,
    "ansiyellow": 43,
    "ansiblue": 44,
    "ansimagenta": 45,
    "ansicyan": 46,
    "ansigray": 47,
    # High intensity.
    "ansibrightblack": 100,
    "ansibrightred": 101,
    "ansibrightgreen": 102,
    "ansibrightyellow": 103,
    "ansibrightblue": 104,
    "ansibrightmagenta": 105,
    "ansibrightcyan": 106,
    "ansiwhite": 107,
}


ANSI_COLORS_TO_RGB = {
    "ansidefault": (
        0x00,
        0x00,
        0x00,
    ),  # Don't use, 'default' doesn't really have a value.
    "ansiblack": (0x00, 0x00, 0x00),
    "ansigray": (0xE5, 0xE5, 0xE5),
    "ansibrightblack": (0x7F, 0x7F, 0x7F),
    "ansiwhite": (0xFF, 0xFF, 0xFF),
    # Low intensity.
    "ansired": (0xCD, 0x00, 0x00),
    "ansigreen": (0x00, 0xCD, 0x00),
    "ansiyellow": (0xCD, 0xCD, 0x00),
    "ansiblue": (0x00, 0x00, 0xCD),
    "ansimagenta": (0xCD, 0x00, 0xCD),
    "ansicyan": (0x00, 0xCD, 0xCD),
    # High intensity.
    "ansibrightred": (0xFF, 0x00, 0x00),
    "ansibrightgreen": (0x00, 0xFF, 0x00),
    "ansibrightyellow": (0xFF, 0xFF, 0x00),
    "ansibrightblue": (0x00, 0x00, 0xFF),
    "ansibrightmagenta": (0xFF, 0x00, 0xFF),
    "ansibrightcyan": (0x00, 0xFF, 0xFF),
}


assert set(FG_ANSI_COLORS) == set(ANSI_COLOR_NAMES)
assert set(BG_ANSI_COLORS) == set(ANSI_COLOR_NAMES)
assert set(ANSI_COLORS_TO_RGB) == set(ANSI_COLOR_NAMES)


def _get_closest_ansi_color(r: int, g: int, b: int, exclude: Sequence[str] = ()) -> str:
    """
    Find closest ANSI color. Return it by name.

    :param r: Red (Between 0 and 255.)
    :param g: Green (Between 0 and 255.)
    :param b: Blue (Between 0 and 255.)
```
