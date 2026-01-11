# Chunk: 658fbdbedb2b_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rust.py`
- lines: 131-223
- chunk: 3/3

```
0-9_]+)', Number.Float,
             'number_lit'),
            (r'[0-9][0-9_]*', Number.Integer, 'number_lit'),

            # String literals
            (r'b"', String, 'bytestring'),
            (r'"', String, 'string'),
            (r'(?s)b?r(#*)".*?"\1', String),

            # Lifetime names
            (r"'", Operator, 'lifetime'),

            # Operators and Punctuation
            (r'\.\.=?', Operator),
            (r'[{}()\[\],.;]', Punctuation),
            (r'[+\-*/%&|<>^!~@=:?]', Operator),

            # Identifiers
            (r'[a-zA-Z_]\w*', Name),
            # Raw identifiers
            (r'r#[a-zA-Z_]\w*', Name),

            # Attributes
            (r'#!?\[', Comment.Preproc, 'attribute['),

            # Misc
            # Lone hashes: not used in Rust syntax, but allowed in macro
            # arguments, most famously for quote::quote!()
            (r'#', Punctuation),
        ],
        'comment': [
            (r'[^*/]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        'doccomment': [
            (r'[^*/]+', String.Doc),
            (r'/\*', String.Doc, '#push'),
            (r'\*/', String.Doc, '#pop'),
            (r'[*/]', String.Doc),
        ],
        'modname': [
            (r'\s+', Whitespace),
            (r'[a-zA-Z_]\w*', Name.Namespace, '#pop'),
            default('#pop'),
        ],
        'funcname': [
            (r'\s+', Whitespace),
            (r'[a-zA-Z_]\w*', Name.Function, '#pop'),
            default('#pop'),
        ],
        'typename': [
            (r'\s+', Whitespace),
            (r'&', Keyword.Pseudo),
            (r"'", Operator, 'lifetime'),
            builtin_funcs_types,
            keyword_types,
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            default('#pop'),
        ],
        'lifetime': [
            (r"(static|_)", Name.Builtin),
            (r"[a-zA-Z_]+\w*", Name.Attribute),
            default('#pop'),
        ],
        'number_lit': [
            (r'[ui](8|16|32|64|size)', Keyword, '#pop'),
            (r'f(32|64)', Keyword, '#pop'),
            default('#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r"""\\['"\\nrt]|\\x[0-7][0-9a-fA-F]|\\0"""
             r"""|\\u\{[0-9a-fA-F]{1,6}\}""", String.Escape),
            (r'[^\\"]+', String),
            (r'\\', String),
        ],
        'bytestring': [
            (r"""\\x[89a-fA-F][0-9a-fA-F]""", String.Escape),
            include('string'),
        ],
        'attribute_common': [
            (r'"', String, 'string'),
            (r'\[', Comment.Preproc, 'attribute['),
        ],
        'attribute[': [
            include('attribute_common'),
            (r'\]', Comment.Preproc, '#pop'),
            (r'[^"\]\[]+', Comment.Preproc),
        ],
    }
```
