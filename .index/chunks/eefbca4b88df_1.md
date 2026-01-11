# Chunk: eefbca4b88df_1

- source: `.venv-lab/Lib/site-packages/nbconvert/filters/highlight.py`
- lines: 90-177
- chunk: 2/3

```
LatexFormatter class.
        See available list in https://pygments.org/docs/formatters/#LatexFormatter
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

    def __call__(self, source, language=None, metadata=None, strip_verbatim=False):
        """
        Return a syntax-highlighted version of the input source as latex output.

        Parameters
        ----------
        source : str
            source of the cell to highlight
        language : str
            language to highlight the syntax of
        metadata : NotebookNode cell metadata
            metadata of the cell to highlight
        strip_verbatim : bool
            remove the Verbatim environment that pygments provides by default
        """
        from pygments.formatters import LatexFormatter

        if not language:
            language = self.pygments_lexer

        latex = _pygments_highlight(
            source, LatexFormatter(**self.extra_formatter_options), language, metadata
        )
        if strip_verbatim:
            latex = latex.replace(r"\begin{Verbatim}[commandchars=\\\{\}]" + "\n", "")
            return latex.replace("\n\\end{Verbatim}\n", "")
        return latex


def _pygments_highlight(
    source, output_formatter, language="ipython", metadata=None, **lexer_options
):
    """
    Return a syntax-highlighted version of the input source

    Parameters
    ----------
    source : str
        source of the cell to highlight
    output_formatter : Pygments formatter
    language : str
        language to highlight the syntax of
    metadata : NotebookNode cell metadata
        metadata of the cell to highlight
    lexer_options : dict
        Options to pass to the pygments lexer. See
        https://pygments.org/docs/lexers/#available-lexers for more information about
        valid lexer options
    """
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound

    # If the cell uses a magic extension language,
    # use the magic language instead.
    if language.startswith("ipython") and metadata and "magics_language" in metadata:
        language = metadata["magics_language"]

    lexer = None
    if language == "ipython2":
        try:
            from IPython.lib.lexers import IPythonLexer
        except ImportError:
            warn("IPython lexer unavailable, falling back on Python", stacklevel=2)
            language = "python"
        else:
            lexer = IPythonLexer()
```
