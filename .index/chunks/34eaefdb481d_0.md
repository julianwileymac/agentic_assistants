# Chunk: 34eaefdb481d_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/nix.py`
- lines: 1-102
- chunk: 1/2

```
"""
    pygments.lexers.nix
    ~~~~~~~~~~~~~~~~~~~

    Lexers for the NixOS Nix language.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Literal

__all__ = ['NixLexer']


class NixLexer(RegexLexer):
    """
    For the Nix language.
    """

    name = 'Nix'
    url = 'http://nixos.org/nix/'
    aliases = ['nixos', 'nix']
    filenames = ['*.nix']
    mimetypes = ['text/x-nix']
    version_added = '2.0'

    keywords = ['rec', 'with', 'let', 'in', 'inherit', 'assert', 'if',
                'else', 'then', '...']
    builtins = ['import', 'abort', 'baseNameOf', 'dirOf', 'isNull', 'builtins',
                'map', 'removeAttrs', 'throw', 'toString', 'derivation']
    operators = ['++', '+', '?', '.', '!', '//', '==', '/',
                 '!=', '&&', '||', '->', '=', '<', '>', '*', '-']

    punctuations = ["(", ")", "[", "]", ";", "{", "}", ":", ",", "@"]

    tokens = {
        'root': [
            # comments starting with #
            (r'#.*$', Comment.Single),

            # multiline comments
            (r'/\*', Comment.Multiline, 'comment'),

            # whitespace
            (r'\s+', Text),

            # keywords
            ('({})'.format('|'.join(re.escape(entry) + '\\b' for entry in keywords)), Keyword),

            # highlight the builtins
            ('({})'.format('|'.join(re.escape(entry) + '\\b' for entry in builtins)),
             Name.Builtin),

            (r'\b(true|false|null)\b', Name.Constant),

            # floats
            (r'-?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?', Number.Float),

            # integers
            (r'-?[0-9]+', Number.Integer),

            # paths
            (r'[\w.+-]*(\/[\w.+-]+)+', Literal),
            (r'~(\/[\w.+-]+)+', Literal),
            (r'\<[\w.+-]+(\/[\w.+-]+)*\>', Literal),

            # operators
            ('({})'.format('|'.join(re.escape(entry) for entry in operators)),
             Operator),

            # word operators
            (r'\b(or|and)\b', Operator.Word),

            (r'\{', Punctuation, 'block'),

            # punctuations
            ('({})'.format('|'.join(re.escape(entry) for entry in punctuations)), Punctuation),

            # strings
            (r'"', String.Double, 'doublequote'),
            (r"''", String.Multiline, 'multiline'),

            # urls
            (r'[a-zA-Z][a-zA-Z0-9\+\-\.]*\:[\w%/?:@&=+$,\\.!~*\'-]+', Literal),

            # names of variables
            (r'[\w-]+(?=\s*=)', String.Symbol),
            (r'[a-zA-Z_][\w\'-]*', Text),

            (r"\$\{", String.Interpol, 'antiquote'),
        ],
        'comment': [
            (r'[^/*]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
```
