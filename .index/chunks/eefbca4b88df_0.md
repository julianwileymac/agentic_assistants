# Chunk: eefbca4b88df_0

- source: `.venv-lab/Lib/site-packages/nbconvert/filters/highlight.py`
- lines: 1-99
- chunk: 1/3

```
"""
Module containing filter functions that allow code to be highlighted
from within Jinja templates.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

# pygments must not be imported at the module level
# because errors should be raised at runtime if it's actually needed,
# not import time, when it may not be needed.

from html import escape
from warnings import warn

from traitlets import Dict, observe

from nbconvert.utils.base import NbConvertBase

MULTILINE_OUTPUTS = ["text", "html", "svg", "latex", "javascript", "json"]

__all__ = ["Highlight2HTML", "Highlight2Latex"]


class Highlight2HTML(NbConvertBase):
    """Convert highlighted code to html."""

    extra_formatter_options = Dict(
        {},
        help="""
        Extra set of options to control how code is highlighted.

        Passed through to the pygments' HtmlFormatter class.
        See available list in https://pygments.org/docs/formatters/#HtmlFormatter
        """,
        config=True,
    )

    def __init__(self, pygments_lexer=None, **kwargs):
        """Initialize the converter."""
        self.pygments_lexer = pygments_lexer or "ipython3"
        super().__init__(**kwargs)

    @observe("default_language")
    def _default_language_changed(self, change):
        warn(
            "Setting default_language in config is deprecated as of 5.0, "
            "please use language_info metadata instead.",
            stacklevel=2,
        )
        self.pygments_lexer = change["new"]

    def __call__(self, source, language=None, metadata=None):
        """
        Return a syntax-highlighted version of the input source as html output.

        Parameters
        ----------
        source : str
            source of the cell to highlight
        language : str
            language to highlight the syntax of
        metadata : NotebookNode cell metadata
            metadata of the cell to highlight
        """
        from pygments.formatters import HtmlFormatter

        if not language:
            language = self.pygments_lexer

        return _pygments_highlight(
            source if len(source) > 0 else " ",
            # needed to help post processors:
            HtmlFormatter(
                cssclass=escape(f" highlight hl-{language}"), **self.extra_formatter_options
            ),
            language,
            metadata,
        )


class Highlight2Latex(NbConvertBase):
    """Convert highlighted code to latex."""

    extra_formatter_options = Dict(
        {},
        help="""
        Extra set of options to control how code is highlighted.

        Passed through to the pygments' LatexFormatter class.
        See available list in https://pygments.org/docs/formatters/#LatexFormatter
        """,
        config=True,
    )

    def __init__(self, pygments_lexer=None, **kwargs):
        """Initialize the converter."""
        self.pygments_lexer = pygments_lexer or "ipython3"
```
