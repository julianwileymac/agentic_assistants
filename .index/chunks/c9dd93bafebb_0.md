# Chunk: c9dd93bafebb_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/lilypond.py`
- lines: 1-83
- chunk: 1/4

```
"""
    pygments.lexers.lilypond
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexer for LilyPond.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import bygroups, default, inherit, words
from pygments.lexers.lisp import SchemeLexer
from pygments.lexers._lilypond_builtins import (
    keywords, pitch_language_names, clefs, scales, repeat_types, units,
    chord_modifiers, pitches, music_functions, dynamics, articulations,
    music_commands, markup_commands, grobs, translators, contexts,
    context_properties, grob_properties, scheme_functions, paper_variables,
    header_variables
)
from pygments.token import Token

__all__ = ["LilyPondLexer"]

# In LilyPond, (unquoted) name tokens only contain letters, hyphens,
# and underscores, where hyphens and underscores must not start or end
# a name token.
#
# Note that many of the entities listed as LilyPond built-in keywords
# (in file `_lilypond_builtins.py`) are only valid if surrounded by
# double quotes, for example, 'hufnagel-fa1'. This means that
# `NAME_END_RE` doesn't apply to such entities in valid LilyPond code.
NAME_END_RE = r"(?=\d|[^\w\-]|[\-_][\W\d])"

def builtin_words(names, backslash, suffix=NAME_END_RE):
    prefix = r"[\-_^]?"
    if backslash == "mandatory":
        prefix += r"\\"
    elif backslash == "optional":
        prefix += r"\\?"
    else:
        assert backslash == "disallowed"
    return words(names, prefix, suffix)


class LilyPondLexer(SchemeLexer):
    """
    Lexer for input to LilyPond, a text-based music typesetter.

    .. important::

       This lexer is meant to be used in conjunction with the ``lilypond`` style.
    """
    name = 'LilyPond'
    url = 'https://lilypond.org'
    aliases = ['lilypond']
    filenames = ['*.ly']
    mimetypes = []
    version_added = '2.11'

    flags = re.DOTALL | re.MULTILINE

    # Because parsing LilyPond input is very tricky (and in fact
    # impossible without executing LilyPond when there is Scheme
    # code in the file), this lexer does not try to recognize
    # lexical modes. Instead, it catches the most frequent pieces
    # of syntax, and, above all, knows about many kinds of builtins.

    # In order to parse embedded Scheme, this lexer subclasses the SchemeLexer.
    # It redefines the 'root' state entirely, and adds a rule for #{ #}
    # to the 'value' state. The latter is used to parse a Scheme expression
    # after #.

    def get_tokens_unprocessed(self, text):
        """Highlight Scheme variables as LilyPond builtins when applicable."""
        for index, token, value in super().get_tokens_unprocessed(text):
            if token is Token.Name.Function or token is Token.Name.Variable:
                if value in scheme_functions:
                    token = Token.Name.Builtin.SchemeFunction
            elif token is Token.Name.Builtin:
                token = Token.Name.Builtin.SchemeBuiltin
```
