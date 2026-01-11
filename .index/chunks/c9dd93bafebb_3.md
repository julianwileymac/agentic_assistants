# Chunk: c9dd93bafebb_3

- source: `.venv-lab/Lib/site-packages/pygments/lexers/lilypond.py`
- lines: 185-226
- chunk: 4/4

```
rVariable),

            # Other backslashed-escaped names (like dereferencing a
            # music variable), possibly with a direction specifier.
            (r"[\-_^]?\\.+?" + NAME_END_RE, Token.Name.BackslashReference),

            # Definition of a variable. Support assignments to alist keys
            # (myAlist.my-key.my-nested-key = \markup \spam \eggs).
            (r"""(?x)
               (?: [^\W\d] | - )+
               (?= (?: [^\W\d] | [\-.] )* \s* = )
              """, Token.Name.Lvalue),

            # Virtually everything can appear in markup mode, so we highlight
            # as text.  Try to get a complete word, or we might wrongly lex
            # a suffix that happens to be a builtin as a builtin (e.g., "myStaff").
            (r"([^\W\d]|-)+?" + NAME_END_RE, Token.Text),
            (r".", Token.Text),
        ],
        "string": [
            (r'"', Token.String, "#pop"),
            (r'\\.', Token.String.Escape),
            (r'[^\\"]+', Token.String),
        ],
        "value": [
            # Scan a LilyPond value, then pop back since we had a
            # complete expression.
            (r"#\{", Token.Punctuation, ("#pop", "root")),
            inherit,
        ],
        # Grob subproperties are undeclared and it would be tedious
        # to maintain them by hand. Instead, this state allows recognizing
        # everything that looks like a-known-property.foo.bar-baz as
        # one single property name.
        "maybe-subproperties": [
            (r"\s+", Token.Text.Whitespace),
            (r"(\.)((?:[^\W\d]|-)+?)" + NAME_END_RE,
             bygroups(Token.Punctuation, Token.Name.Builtin.GrobProperty)),
            default("#pop"),
        ]
    }
```
