# Chunk: 3bfcdcac6ac1_0

- source: `.venv-lab/Lib/site-packages/pygments/lexers/graphql.py`
- lines: 1-109
- chunk: 1/2

```
"""
    pygments.lexers.graphql
    ~~~~~~~~~~~~~~~~~~~~~~~

    Lexer for GraphQL, an open-source data query and manipulation
    language for APIs.

    More information:
    https://graphql.org/

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, words, include, bygroups, default
from pygments.token import (Comment, Keyword, Name, Number, Punctuation, String,
                            Whitespace)


__all__ = ["GraphQLLexer"]

OPERATION_TYPES = ("query", "mutation", "subscription")
BUILTIN_TYPES = ("Int", "Float", "String", "Boolean", "ID")
BOOLEAN_VALUES = ("true", "false", "null")
KEYWORDS = (
    "type",
    "schema",
    "extend",
    "enum",
    "scalar",
    "implements",
    "interface",
    "union",
    "input",
    "directive",
    "QUERY",
    "MUTATION",
    "SUBSCRIPTION",
    "FIELD",
    "FRAGMENT_DEFINITION",
    "FRAGMENT_SPREAD",
    "INLINE_FRAGMENT",
    "SCHEMA",
    "SCALAR",
    "OBJECT",
    "FIELD_DEFINITION",
    "ARGUMENT_DEFINITION",
    "INTERFACE",
    "UNION",
    "ENUM",
    "ENUM_VALUE",
    "INPUT_OBJECT",
    "INPUT_FIELD_DEFINITION",
)


class GraphQLLexer(RegexLexer):
    """
    Lexer for GraphQL syntax
    """
    name = "GraphQL"
    aliases = ["graphql"]
    filenames = ["*.graphql"]
    url = "https://graphql.org"
    version_added = '2.16'

    tokens = {
        "ignored_tokens": [
            (r"\s+", Whitespace),  # Whitespaces
            (r"#.*$", Comment),
            (",", Punctuation),  # Insignificant commas
        ],
        "value": [
            include("ignored_tokens"),
            (r"-?\d+(?![.eE])", Number.Integer, "#pop"),
            (
                r"-?\d+(\.\d+)?([eE][+-]?\d+)?",
                Number.Float,
                "#pop",
            ),
            (r'"', String, ("#pop", "string")),
            (words(BOOLEAN_VALUES, suffix=r"\b"), Name.Builtin, "#pop"),
            (r"\$[a-zA-Z_]\w*", Name.Variable, "#pop"),
            (r"[a-zA-Z_]\w*", Name.Constant, "#pop"),
            (r"\[", Punctuation, ("#pop", "list_value")),
            (r"\{", Punctuation, ("#pop", "object_value")),
        ],
        "list_value": [
            include("ignored_tokens"),
            ("]", Punctuation, "#pop"),
            default("value"),
        ],
        "object_value": [
            include("ignored_tokens"),
            (r"[a-zA-Z_]\w*", Name),
            (r":", Punctuation, "value"),
            (r"\}", Punctuation, "#pop"),
        ],
        "string": [
            (r'\\(["\\/bfnrt]|u[a-fA-F0-9]{4})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'"', String, "#pop"),
        ],
        "root": [
            include("ignored_tokens"),
            (words(OPERATION_TYPES, suffix=r"\b"), Keyword, "operation"),
            (words(KEYWORDS, suffix=r"\b"), Keyword),
            (r"\{", Punctuation, "selection_set"),
```
