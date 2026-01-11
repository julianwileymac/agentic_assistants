# Chunk: b86eb5ec4e5a_8

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ruby.py`
- lines: 491-519
- chunk: 9/9

```
'Object', 'Array', 'Hash', 'Directory', 'File', 'Class', 'String',
                'Number', 'Enumerable', 'FancyEnumerable', 'Block', 'TrueClass',
                'NilClass', 'FalseClass', 'Tuple', 'Symbol', 'Stack', 'Set',
                'FancySpec', 'Method', 'Package', 'Range'), suffix=r'\b'),
             Name.Builtin),
            # functions
            (r'[a-zA-Z](\w|[-+?!=*/^><%])*:', Name.Function),
            # operators, must be below functions
            (r'[-+*/~,<>=&!?%^\[\].$]+', Operator),
            (r'[A-Z]\w*', Name.Constant),
            (r'@[a-zA-Z_]\w*', Name.Variable.Instance),
            (r'@@[a-zA-Z_]\w*', Name.Variable.Class),
            ('@@?', Operator),
            (r'[a-zA-Z_]\w*', Name),
            # numbers - / checks are necessary to avoid mismarking regexes,
            # see comment in RubyLexer
            (r'(0[oO]?[0-7]+(?:_[0-7]+)*)(\s*)([/?])?',
             bygroups(Number.Oct, Whitespace, Operator)),
            (r'(0[xX][0-9A-Fa-f]+(?:_[0-9A-Fa-f]+)*)(\s*)([/?])?',
             bygroups(Number.Hex, Whitespace, Operator)),
            (r'(0[bB][01]+(?:_[01]+)*)(\s*)([/?])?',
             bygroups(Number.Bin, Whitespace, Operator)),
            (r'([\d]+(?:_\d+)*)(\s*)([/?])?',
             bygroups(Number.Integer, Whitespace, Operator)),
            (r'\d+([eE][+-]?[0-9]+)|\d+\.\d+([eE][+-]?[0-9]+)?', Number.Float),
            (r'\d+', Number.Integer)
        ]
    }
```
