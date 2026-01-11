# Chunk: c86adfde1dfb_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/mime.py`
- lines: 1-88
- chunk: 1/3

```
"""
    pygments.lexers.mime
    ~~~~~~~~~~~~~~~~~~~~

    Lexer for Multipurpose Internet Mail Extensions (MIME) data.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, include
from pygments.lexers import get_lexer_for_mimetype
from pygments.token import Text, Name, String, Operator, Comment, Other
from pygments.util import get_int_opt, ClassNotFound

__all__ = ["MIMELexer"]


class MIMELexer(RegexLexer):
    """
    Lexer for Multipurpose Internet Mail Extensions (MIME) data. This lexer is
    designed to process nested multipart data.

    It assumes that the given data contains both header and body (and is
    split at an empty line). If no valid header is found, then the entire data
    will be treated as body.

    Additional options accepted:

    `MIME-max-level`
        Max recursion level for nested MIME structure. Any negative number
        would treated as unlimited. (default: -1)

    `Content-Type`
        Treat the data as a specific content type. Useful when header is
        missing, or this lexer would try to parse from header. (default:
        `text/plain`)

    `Multipart-Boundary`
        Set the default multipart boundary delimiter. This option is only used
        when `Content-Type` is `multipart` and header is missing. This lexer
        would try to parse from header by default. (default: None)

    `Content-Transfer-Encoding`
        Treat the data as a specific encoding. Or this lexer would try to parse
        from header by default. (default: None)
    """

    name = "MIME"
    aliases = ["mime"]
    mimetypes = ["multipart/mixed",
                 "multipart/related",
                 "multipart/alternative"]
    url = 'https://en.wikipedia.org/wiki/MIME'
    version_added = '2.5'

    def __init__(self, **options):
        super().__init__(**options)
        self.boundary = options.get("Multipart-Boundary")
        self.content_transfer_encoding = options.get("Content_Transfer_Encoding")
        self.content_type = options.get("Content_Type", "text/plain")
        self.max_nested_level = get_int_opt(options, "MIME-max-level", -1)

    def get_header_tokens(self, match):
        field = match.group(1)

        if field.lower() in self.attention_headers:
            yield match.start(1), Name.Tag, field + ":"
            yield match.start(2), Text.Whitespace, match.group(2)

            pos = match.end(2)
            body = match.group(3)
            for i, t, v in self.get_tokens_unprocessed(body, ("root", field.lower())):
                yield pos + i, t, v

        else:
            yield match.start(), Comment, match.group()

    def get_body_tokens(self, match):
        pos_body_start = match.start()
        entire_body = match.group()

        # skip first newline
        if entire_body[0] == '\n':
            yield pos_body_start, Text.Whitespace, '\n'
```
