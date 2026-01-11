# Chunk: 658fbdbedb2b_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rust.py`
- lines: 73-141
- chunk: 2/3

```
: [
            # Whitespace and Comments
            (r'\n', Whitespace),
            (r'\s+', Whitespace),
            (r'//!.*?\n', String.Doc),
            (r'///(\n|[^/].*?\n)', String.Doc),
            (r'//(.*?)\n', Comment.Single),
            (r'/\*\*(\n|[^/*])', String.Doc, 'doccomment'),
            (r'/\*!', String.Doc, 'doccomment'),
            (r'/\*', Comment.Multiline, 'comment'),

            # Macro parameters
            (r"""\$([a-zA-Z_]\w*|\(,?|\),?|,?)""", Comment.Preproc),
            # Keywords
            (words(('as', 'async', 'await', 'box', 'const', 'crate', 'dyn',
                    'else', 'extern', 'for', 'if', 'impl', 'in', 'loop',
                    'match', 'move', 'mut', 'pub', 'ref', 'return', 'static',
                    'super', 'trait', 'unsafe', 'use', 'where', 'while'),
                   suffix=r'\b'), Keyword),
            (words(('abstract', 'become', 'do', 'final', 'macro', 'override',
                    'priv', 'typeof', 'try', 'unsized', 'virtual', 'yield'),
                   suffix=r'\b'), Keyword.Reserved),
            (r'(true|false)\b', Keyword.Constant),
            (r'self\b', Name.Builtin.Pseudo),
            (r'mod\b', Keyword, 'modname'),
            (r'let\b', Keyword.Declaration),
            (r'fn\b', Keyword, 'funcname'),
            (r'(struct|enum|type|union)\b', Keyword, 'typename'),
            (r'(default)(\s+)(type|fn)\b', bygroups(Keyword, Whitespace, Keyword)),
            keyword_types,
            (r'[sS]elf\b', Name.Builtin.Pseudo),
            # Prelude (taken from Rust's src/libstd/prelude.rs)
            builtin_funcs_types,
            builtin_macros,
            # Path separators, so types don't catch them.
            (r'::\b', Punctuation),
            # Types in positions.
            (r'(?::|->)', Punctuation, 'typename'),
            # Labels
            (r'(break|continue)(\b\s*)(\'[A-Za-z_]\w*)?',
             bygroups(Keyword, Text.Whitespace, Name.Label)),

            # Character literals
            (r"""'(\\['"\\nrt]|\\x[0-7][0-9a-fA-F]|\\0"""
             r"""|\\u\{[0-9a-fA-F]{1,6}\}|.)'""",
             String.Char),
            (r"""b'(\\['"\\nrt]|\\x[0-9a-fA-F]{2}|\\0"""
             r"""|\\u\{[0-9a-fA-F]{1,6}\}|.)'""",
             String.Char),

            # Binary literals
            (r'0b[01_]+', Number.Bin, 'number_lit'),
            # Octal literals
            (r'0o[0-7_]+', Number.Oct, 'number_lit'),
            # Hexadecimal literals
            (r'0[xX][0-9a-fA-F_]+', Number.Hex, 'number_lit'),
            # Decimal literals
            (r'[0-9][0-9_]*(\.[0-9_]+[eE][+\-]?[0-9_]+|'
             r'\.[0-9_]*(?!\.)|[eE][+\-]?[0-9_]+)', Number.Float,
             'number_lit'),
            (r'[0-9][0-9_]*', Number.Integer, 'number_lit'),

            # String literals
            (r'b"', String, 'bytestring'),
            (r'"', String, 'string'),
            (r'(?s)b?r(#*)".*?"\1', String),

            # Lifetime names
```
