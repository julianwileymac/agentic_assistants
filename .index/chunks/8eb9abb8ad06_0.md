# Chunk: 8eb9abb8ad06_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/savi.py`
- lines: 1-103
- chunk: 1/2

```
"""
    pygments.lexers.savi
    ~~~~~~~~~~~~~~~~~~~~

    Lexer for Savi.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Whitespace, Keyword, Name, String, Number, \
  Operator, Punctuation, Comment, Generic, Error

__all__ = ['SaviLexer']


# The canonical version of this file can be found in the following repository,
# where it is kept in sync with any language changes, as well as the other
# pygments-like lexers that are maintained for use with other tools:
# - https://github.com/savi-lang/savi/blob/main/tooling/pygments/lexers/savi.py
#
# If you're changing this file in the pygments repository, please ensure that
# any changes you make are also propagated to the official Savi repository,
# in order to avoid accidental clobbering of your changes later when an update
# from the Savi repository flows forward into the pygments repository.
#
# If you're changing this file in the Savi repository, please ensure that
# any changes you make are also reflected in the other pygments-like lexers
# (rouge, vscode, etc) so that all of the lexers can be kept cleanly in sync.

class SaviLexer(RegexLexer):
    """
    For Savi source code.

    .. versionadded: 2.10
    """

    name = 'Savi'
    url = 'https://github.com/savi-lang/savi'
    aliases = ['savi']
    filenames = ['*.savi']
    version_added = ''

    tokens = {
      "root": [
        # Line Comment
        (r'//.*?$', Comment.Single),

        # Doc Comment
        (r'::.*?$', Comment.Single),

        # Capability Operator
        (r'(\')(\w+)(?=[^\'])', bygroups(Operator, Name)),

        # Double-Quote String
        (r'\w?"', String.Double, "string.double"),

        # Single-Char String
        (r"'", String.Char, "string.char"),

        # Type Name
        (r'(_?[A-Z]\w*)', Name.Class),

        # Nested Type Name
        (r'(\.)(\s*)(_?[A-Z]\w*)', bygroups(Punctuation, Whitespace, Name.Class)),

        # Declare
        (r'^([ \t]*)(:\w+)',
          bygroups(Whitespace, Name.Tag),
          "decl"),

        # Error-Raising Calls/Names
        (r'((\w+|\+|\-|\*)\!)', Generic.Deleted),

        # Numeric Values
        (r'\b\d([\d_]*(\.[\d_]+)?)\b', Number),

        # Hex Numeric Values
        (r'\b0x([0-9a-fA-F_]+)\b', Number.Hex),

        # Binary Numeric Values
        (r'\b0b([01_]+)\b', Number.Bin),

        # Function Call (with braces)
        (r'\w+(?=\()', Name.Function),

        # Function Call (with receiver)
        (r'(\.)(\s*)(\w+)', bygroups(Punctuation, Whitespace, Name.Function)),

        # Function Call (with self receiver)
        (r'(@)(\w+)', bygroups(Punctuation, Name.Function)),

        # Parenthesis
        (r'\(', Punctuation, "root"),
        (r'\)', Punctuation, "#pop"),

        # Brace
        (r'\{', Punctuation, "root"),
        (r'\}', Punctuation, "#pop"),

        # Bracket
```
