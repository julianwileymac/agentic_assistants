# Chunk: 5acec92b1cb4_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/gdscript.py`
- lines: 1-87
- chunk: 1/3

```
"""
    pygments.lexers.gdscript
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexer for GDScript.

    Modified by Daniel J. Ramirez <djrmuv@gmail.com> based on the original
    python.py.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, default, words, \
    combined
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace

__all__ = ["GDScriptLexer"]


class GDScriptLexer(RegexLexer):
    """
    For GDScript source code.
    """

    name = "GDScript"
    url = 'https://www.godotengine.org'
    aliases = ["gdscript", "gd"]
    filenames = ["*.gd"]
    mimetypes = ["text/x-gdscript", "application/x-gdscript"]
    version_added = ''

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting
            (r"%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?"
             "[hlL]?[E-GXc-giorsux%]",
             String.Interpol),
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r"%", ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        "root": [
            (r"\n", Whitespace),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Whitespace, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Whitespace, String.Affix, String.Doc)),
            (r"[^\S\n]+", Whitespace),
            (r"#.*$", Comment.Single),
            (r"[]{}:(),;[]", Punctuation),
            (r"(\\)(\n)", bygroups(Text, Whitespace)),
            (r"\\", Text),
            (r"(in|and|or|not)\b", Operator.Word),
            (r"!=|==|<<|>>|&&|\+=|-=|\*=|/=|%=|&=|\|=|\|\||[-~+/*%=<>&^.!|$]",
             Operator),
            include("keywords"),
            (r"(func)(\s+)", bygroups(Keyword, Whitespace), "funcname"),
            (r"(class)(\s+)", bygroups(Keyword, Whitespace), "classname"),
            include("builtins"),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(""")',
             bygroups(String.Affix, String.Double),
             "tdqs"),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(''')",
             bygroups(String.Affix, String.Single),
             "tsqs"),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(")',
             bygroups(String.Affix, String.Double),
             "dqs"),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(')",
             bygroups(String.Affix, String.Single),
             "sqs"),
            ('([uUbB]?)(""")',
             bygroups(String.Affix, String.Double),
             combined("stringescape", "tdqs")),
            ("([uUbB]?)(''')",
             bygroups(String.Affix, String.Single),
             combined("stringescape", "tsqs")),
```
