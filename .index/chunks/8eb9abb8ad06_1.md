# Chunk: 8eb9abb8ad06_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/savi.py`
- lines: 91-172
- chunk: 2/2

```
n Call (with self receiver)
        (r'(@)(\w+)', bygroups(Punctuation, Name.Function)),

        # Parenthesis
        (r'\(', Punctuation, "root"),
        (r'\)', Punctuation, "#pop"),

        # Brace
        (r'\{', Punctuation, "root"),
        (r'\}', Punctuation, "#pop"),

        # Bracket
        (r'\[', Punctuation, "root"),
        (r'(\])(\!)', bygroups(Punctuation, Generic.Deleted), "#pop"),
        (r'\]', Punctuation, "#pop"),

        # Punctuation
        (r'[,;:\.@]', Punctuation),

        # Piping Operators
        (r'(\|\>)', Operator),

        # Branching Operators
        (r'(\&\&|\|\||\?\?|\&\?|\|\?|\.\?)', Operator),

        # Comparison Operators
        (r'(\<\=\>|\=\~|\=\=|\<\=|\>\=|\<|\>)', Operator),

        # Arithmetic Operators
        (r'(\+|\-|\/|\*|\%)', Operator),

        # Assignment Operators
        (r'(\=)', Operator),

        # Other Operators
        (r'(\!|\<\<|\<|\&|\|)', Operator),

        # Identifiers
        (r'\b\w+\b', Name),

        # Whitespace
        (r'[ \t\r]+\n*|\n+', Whitespace),
      ],

      # Declare (nested rules)
      "decl": [
        (r'\b[a-z_]\w*\b(?!\!)', Keyword.Declaration),
        (r':', Punctuation, "#pop"),
        (r'\n', Whitespace, "#pop"),
        include("root"),
      ],

      # Double-Quote String (nested rules)
      "string.double": [
        (r'\\\(', String.Interpol, "string.interpolation"),
        (r'\\u[0-9a-fA-F]{4}', String.Escape),
        (r'\\x[0-9a-fA-F]{2}', String.Escape),
        (r'\\[bfnrt\\\']', String.Escape),
        (r'\\"', String.Escape),
        (r'"', String.Double, "#pop"),
        (r'[^\\"]+', String.Double),
        (r'.', Error),
      ],

      # Single-Char String (nested rules)
      "string.char": [
        (r'\\u[0-9a-fA-F]{4}', String.Escape),
        (r'\\x[0-9a-fA-F]{2}', String.Escape),
        (r'\\[bfnrt\\\']', String.Escape),
        (r"\\'", String.Escape),
        (r"'", String.Char, "#pop"),
        (r"[^\\']+", String.Char),
        (r'.', Error),
      ],

      # Interpolation inside String (nested rules)
      "string.interpolation": [
        (r"\)", String.Interpol, "#pop"),
        include("root"),
      ]
    }
```
