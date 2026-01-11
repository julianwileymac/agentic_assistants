# Chunk: b9eda0aa6e39_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/tlb.py`
- lines: 1-60
- chunk: 1/1

```
"""
    pygments.lexers.tlb
    ~~~~~~~~~~~~~~~~~~~

    Lexers for TL-b.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, include, words
from pygments.token import Operator, Name, \
    Number, Whitespace, Punctuation, Comment

__all__ = ['TlbLexer']


class TlbLexer(RegexLexer):
    """
    For TL-b source code.
    """

    name = 'Tl-b'
    aliases = ['tlb']
    filenames = ['*.tlb']
    url = 'https://docs.ton.org/#/overviews/TL-B'
    version_added = ''

    tokens = {
        'root': [
            (r'\s+', Whitespace),

            include('comments'),

            (r'[0-9]+', Number),
            (words((
                '+', '-', '*', '=', '?', '~', '.',
                '^', '==', '<', '>', '<=', '>=', '!='
            )), Operator),
            (words(('##', '#<', '#<=')), Name.Tag),
            (r'#[0-9a-f]*_?', Name.Tag),
            (r'\$[01]*_?', Name.Tag),

            (r'[a-zA-Z_][0-9a-zA-Z_]*', Name),

            (r'[;():\[\]{}]', Punctuation)
        ],

        'comments': [
            (r'//.*', Comment.Singleline),
            (r'/\*', Comment.Multiline, 'comment'),
        ],
        'comment': [
            (r'[^/*]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
    }
```
