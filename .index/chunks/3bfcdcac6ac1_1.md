# Chunk: 3bfcdcac6ac1_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/graphql.py`
- lines: 101-177
- chunk: 2/2

```
other characters
            (r'"', String, "#pop"),
        ],
        "root": [
            include("ignored_tokens"),
            (words(OPERATION_TYPES, suffix=r"\b"), Keyword, "operation"),
            (words(KEYWORDS, suffix=r"\b"), Keyword),
            (r"\{", Punctuation, "selection_set"),
            (r"fragment\b", Keyword, "fragment_definition"),
        ],
        "operation": [
            include("ignored_tokens"),
            (r"[a-zA-Z_]\w*", Name.Function),
            (r"\(", Punctuation, "variable_definition"),
            (r"\{", Punctuation, ("#pop", "selection_set")),
        ],
        "variable_definition": [
            include("ignored_tokens"),
            (r"\$[a-zA-Z_]\w*", Name.Variable),
            (r"[\]!]", Punctuation),
            (r":", Punctuation, "type"),
            (r"=", Punctuation, "value"),
            (r"\)", Punctuation, "#pop"),
        ],
        "type": [
            include("ignored_tokens"),
            (r"\[", Punctuation),
            (words(BUILTIN_TYPES, suffix=r"\b"), Name.Builtin, "#pop"),
            (r"[a-zA-Z_]\w*", Name.Class, "#pop"),
        ],
        "selection_set": [
            include("ignored_tokens"),
            (r"([a-zA-Z_]\w*)(\s*)(:)", bygroups(Name.Label, Whitespace, Punctuation)),
            (r"[a-zA-Z_]\w*", Name),  # Field
            (
                r"(\.\.\.)(\s+)(on)\b",
                bygroups(Punctuation, Whitespace, Keyword),
                "inline_fragment",
            ),
            (r"\.\.\.", Punctuation, "fragment_spread"),
            (r"\(", Punctuation, "arguments"),
            (r"@[a-zA-Z_]\w*", Name.Decorator, "directive"),
            (r"\{", Punctuation, "selection_set"),
            (r"\}", Punctuation, "#pop"),
        ],
        "directive": [
            include("ignored_tokens"),
            (r"\(", Punctuation, ("#pop", "arguments")),
        ],
        "arguments": [
            include("ignored_tokens"),
            (r"[a-zA-Z_]\w*", Name),
            (r":", Punctuation, "value"),
            (r"\)", Punctuation, "#pop"),
        ],
        # Fragments
        "fragment_definition": [
            include("ignored_tokens"),
            (r"[\]!]", Punctuation),  # For NamedType
            (r"on\b", Keyword, "type"),
            (r"[a-zA-Z_]\w*", Name.Function),
            (r"@[a-zA-Z_]\w*", Name.Decorator, "directive"),
            (r"\{", Punctuation, ("#pop", "selection_set")),
        ],
        "fragment_spread": [
            include("ignored_tokens"),
            (r"@[a-zA-Z_]\w*", Name.Decorator, "directive"),
            (r"[a-zA-Z_]\w*", Name, "#pop"),  # Fragment name
        ],
        "inline_fragment": [
            include("ignored_tokens"),
            (r"[a-zA-Z_]\w*", Name.Class),  # Type condition
            (r"@[a-zA-Z_]\w*", Name.Decorator, "directive"),
            (r"\{", Punctuation, ("#pop", "selection_set")),
        ],
    }
```
