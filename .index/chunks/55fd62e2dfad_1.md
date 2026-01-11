# Chunk: 55fd62e2dfad_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/futhark.py`
- lines: 75-106
- chunk: 2/2

```
 num_postfix, Number.Integer),

            #  Character/String Literals
            (r"'", String.Char, 'character'),
            (r'"', String, 'string'),
            #  Special
            (r'\[[a-zA-Z_\d]*\]', Keyword.Type),
            (r'\(\)', Name.Builtin),
        ],
        'character': [
            # Allows multi-chars, incorrectly.
            (r"[^\\']'", String.Char, '#pop'),
            (r"\\", String.Escape, 'escape'),
            ("'", String.Char, '#pop'),
        ],
        'string': [
            (r'[^\\"]+', String),
            (r"\\", String.Escape, 'escape'),
            ('"', String, '#pop'),
        ],

        'escape': [
            (r'[abfnrtv"\'&\\]', String.Escape, '#pop'),
            (r'\^[][' + uni.Lu + r'@^_]', String.Escape, '#pop'),
            ('|'.join(ascii), String.Escape, '#pop'),
            (r'o[0-7]+', String.Escape, '#pop'),
            (r'x[\da-fA-F]+', String.Escape, '#pop'),
            (r'\d+', String.Escape, '#pop'),
            (r'(\s+)(\\)', bygroups(Whitespace, String.Escape), '#pop'),
        ],
    }
```
