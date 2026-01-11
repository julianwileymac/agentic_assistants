# Chunk: b86eb5ec4e5a_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ruby.py`
- lines: 1-82
- chunk: 1/9

```
"""
    pygments.lexers.ruby
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for Ruby and related languages.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, ExtendedRegexLexer, include, \
    bygroups, default, LexerContext, do_insertions, words, line_re
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Error, Generic, Whitespace
from pygments.util import shebang_matches

__all__ = ['RubyLexer', 'RubyConsoleLexer', 'FancyLexer']


RUBY_OPERATORS = (
    '*', '**', '-', '+', '-@', '+@', '/', '%', '&', '|', '^', '`', '~',
    '[]', '[]=', '<<', '>>', '<', '<>', '<=>', '>', '>=', '==', '==='
)


class RubyLexer(ExtendedRegexLexer):
    """
    For Ruby source code.
    """

    name = 'Ruby'
    url = 'http://www.ruby-lang.org'
    aliases = ['ruby', 'rb', 'duby']
    filenames = ['*.rb', '*.rbw', 'Rakefile', '*.rake', '*.gemspec',
                 '*.rbx', '*.duby', 'Gemfile', 'Vagrantfile']
    mimetypes = ['text/x-ruby', 'application/x-ruby']
    version_added = ''

    flags = re.DOTALL | re.MULTILINE

    def heredoc_callback(self, match, ctx):
        # okay, this is the hardest part of parsing Ruby...
        # match: 1 = <<[-~]?, 2 = quote? 3 = name 4 = quote? 5 = rest of line

        start = match.start(1)
        yield start, Operator, match.group(1)        # <<[-~]?
        yield match.start(2), String.Heredoc, match.group(2)   # quote ", ', `
        yield match.start(3), String.Delimiter, match.group(3) # heredoc name
        yield match.start(4), String.Heredoc, match.group(4)   # quote again

        heredocstack = ctx.__dict__.setdefault('heredocstack', [])
        outermost = not bool(heredocstack)
        heredocstack.append((match.group(1) in ('<<-', '<<~'), match.group(3)))

        ctx.pos = match.start(5)
        ctx.end = match.end(5)
        # this may find other heredocs, so limit the recursion depth
        if len(heredocstack) < 100:
            yield from self.get_tokens_unprocessed(context=ctx)
        else:
            yield ctx.pos, String.Heredoc, match.group(5)
        ctx.pos = match.end()

        if outermost:
            # this is the outer heredoc again, now we can process them all
            for tolerant, hdname in heredocstack:
                lines = []
                for match in line_re.finditer(ctx.text, ctx.pos):
                    if tolerant:
                        check = match.group().strip()
                    else:
                        check = match.group().rstrip()
                    if check == hdname:
                        for amatch in lines:
                            yield amatch.start(), String.Heredoc, amatch.group()
                        yield match.start(), String.Delimiter, match.group()
                        ctx.pos = match.end()
                        break
                    else:
```
