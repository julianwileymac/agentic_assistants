# Chunk: 4d19cfd4f7ae_0

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/styles/defaults.py`
- lines: 1-79
- chunk: 1/4

```
"""
The default styling.
"""

from __future__ import annotations

from prompt_toolkit.cache import memoized

from .base import ANSI_COLOR_NAMES, BaseStyle
from .named_colors import NAMED_COLORS
from .style import Style, merge_styles

__all__ = [
    "default_ui_style",
    "default_pygments_style",
]

#: Default styling. Mapping from classnames to their style definition.
PROMPT_TOOLKIT_STYLE = [
    # Highlighting of search matches in document.
    ("search", "bg:ansibrightyellow ansiblack"),
    ("search.current", ""),
    # Incremental search.
    ("incsearch", ""),
    ("incsearch.current", "reverse"),
    # Highlighting of select text in document.
    ("selected", "reverse"),
    ("cursor-column", "bg:#dddddd"),
    ("cursor-line", "underline"),
    ("color-column", "bg:#ccaacc"),
    # Highlighting of matching brackets.
    ("matching-bracket", ""),
    ("matching-bracket.other", "#000000 bg:#aacccc"),
    ("matching-bracket.cursor", "#ff8888 bg:#880000"),
    # Styling of other cursors, in case of block editing.
    ("multiple-cursors", "#000000 bg:#ccccaa"),
    # Line numbers.
    ("line-number", "#888888"),
    ("line-number.current", "bold"),
    ("tilde", "#8888ff"),
    # Default prompt.
    ("prompt", ""),
    ("prompt.arg", "noinherit"),
    ("prompt.arg.text", ""),
    ("prompt.search", "noinherit"),
    ("prompt.search.text", ""),
    # Search toolbar.
    ("search-toolbar", "bold"),
    ("search-toolbar.text", "nobold"),
    # System toolbar
    ("system-toolbar", "bold"),
    ("system-toolbar.text", "nobold"),
    # "arg" toolbar.
    ("arg-toolbar", "bold"),
    ("arg-toolbar.text", "nobold"),
    # Validation toolbar.
    ("validation-toolbar", "bg:#550000 #ffffff"),
    ("window-too-small", "bg:#550000 #ffffff"),
    # Completions toolbar.
    ("completion-toolbar", "bg:#bbbbbb #000000"),
    ("completion-toolbar.arrow", "bg:#bbbbbb #000000 bold"),
    ("completion-toolbar.completion", "bg:#bbbbbb #000000"),
    ("completion-toolbar.completion.current", "bg:#444444 #ffffff"),
    # Completions menu.
    ("completion-menu", "bg:#bbbbbb #000000"),
    ("completion-menu.completion", ""),
    # (Note: for the current completion, we use 'reverse' on top of fg/bg
    # colors. This is to have proper rendering with NO_COLOR=1).
    ("completion-menu.completion.current", "fg:#888888 bg:#ffffff reverse"),
    ("completion-menu.meta.completion", "bg:#999999 #000000"),
    ("completion-menu.meta.completion.current", "bg:#aaaaaa #000000"),
    ("completion-menu.multi-column-meta", "bg:#aaaaaa #000000"),
    # Fuzzy matches in completion menu (for FuzzyCompleter).
    ("completion-menu.completion fuzzymatch.outside", "fg:#444444"),
    ("completion-menu.completion fuzzymatch.inside", "bold"),
    ("completion-menu.completion fuzzymatch.inside.character", "underline"),
    ("completion-menu.completion.current fuzzymatch.outside", "fg:default"),
    ("completion-menu.completion.current fuzzymatch.inside", "nobold"),
```
