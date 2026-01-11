# Chunk: ccc6b5bec4ab_0

- source: `.venv-lab/Lib/site-packages/mistune/plugins/formatting.py`
- lines: 1-92
- chunk: 1/2

```
import re
from typing import TYPE_CHECKING, Match, Optional, Pattern

from ..helpers import PREVENT_BACKSLASH

if TYPE_CHECKING:
    from ..core import BaseRenderer, InlineState
    from ..inline_parser import InlineParser
    from ..markdown import Markdown

__all__ = ["strikethrough", "mark", "insert", "superscript", "subscript"]

_STRIKE_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\~|[^\s~])~~(?!~)")
_MARK_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\=|[^\s=])==(?!=)")
_INSERT_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\^|[^\s^])\^\^(?!\^)")

SUPERSCRIPT_PATTERN = r"\^(?:" + PREVENT_BACKSLASH + r"\\\^|\S|\\ )+?\^"
SUBSCRIPT_PATTERN = r"~(?:" + PREVENT_BACKSLASH + r"\\~|\S|\\ )+?~"


def parse_strikethrough(inline: "InlineParser", m: Match[str], state: "InlineState") -> Optional[int]:
    return _parse_to_end(inline, m, state, "strikethrough", _STRIKE_END)


def render_strikethrough(renderer: "BaseRenderer", text: str) -> str:
    return "<del>" + text + "</del>"


def parse_mark(inline: "InlineParser", m: Match[str], state: "InlineState") -> Optional[int]:
    return _parse_to_end(inline, m, state, "mark", _MARK_END)


def render_mark(renderer: "BaseRenderer", text: str) -> str:
    return "<mark>" + text + "</mark>"


def parse_insert(inline: "InlineParser", m: Match[str], state: "InlineState") -> Optional[int]:
    return _parse_to_end(inline, m, state, "insert", _INSERT_END)


def render_insert(renderer: "BaseRenderer", text: str) -> str:
    return "<ins>" + text + "</ins>"


def parse_superscript(inline: "InlineParser", m: Match[str], state: "InlineState") -> int:
    return _parse_script(inline, m, state, "superscript")


def render_superscript(renderer: "BaseRenderer", text: str) -> str:
    return "<sup>" + text + "</sup>"


def parse_subscript(inline: "InlineParser", m: Match[str], state: "InlineState") -> int:
    return _parse_script(inline, m, state, "subscript")


def render_subscript(renderer: "BaseRenderer", text: str) -> str:
    return "<sub>" + text + "</sub>"


def _parse_to_end(
    inline: "InlineParser",
    m: Match[str],
    state: "InlineState",
    tok_type: str,
    end_pattern: Pattern[str],
) -> Optional[int]:
    pos = m.end()
    m1 = end_pattern.search(state.src, pos)
    if not m1:
        return None
    end_pos = m1.end()
    text = state.src[pos : end_pos - 2]
    new_state = state.copy()
    new_state.src = text
    children = inline.render(new_state)
    state.append_token({"type": tok_type, "children": children})
    return end_pos


def _parse_script(inline: "InlineParser", m: Match[str], state: "InlineState", tok_type: str) -> int:
    text = m.group(0)
    new_state = state.copy()
    new_state.src = text[1:-1].replace("\\ ", " ")
    children = inline.render(new_state)
    state.append_token({"type": tok_type, "children": children})
    return m.end()


def strikethrough(md: "Markdown") -> None:
    """A mistune plugin to support strikethrough. Spec defined by
```
