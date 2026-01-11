# Chunk: 0128bbdea9ab_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/dax.py`
- lines: 86-136
- chunk: 3/3

```
removefilters', 'replace', 'rept', 'right',
                    'rollup', 'rollupaddissubtotal', 'rollupgroup', 'rollupissubtotal',
                    'round', 'rounddown', 'roundup', 'row', 'rri', 'sameperiodlastyear',
                    'sample', 'sampleaxiswithlocalminmax', 'search', 'second',
                    'selectcolumns', 'selectedmeasure', 'selectedmeasureformatstring',
                    'selectedmeasurename', 'selectedvalue', 'sign', 'sin', 'sinh', 'sln',
                    'sqrt', 'sqrtpi', 'startofmonth', 'startofquarter', 'startofyear',
                    'stdev.p', 'stdev.s', 'stdevx.p', 'stdevx.s', 'substitute',
                    'substitutewithindex', 'sum', 'summarize', 'summarizecolumns', 'sumx',
                    'switch', 'syd', 't.dist', 't.dist.2t', 't.dist.rt', 't.inv',
                    't.inv.2t', 'tan', 'tanh', 'tbilleq', 'tbillprice', 'tbillyield',
                    'time', 'timevalue', 'tocsv', 'today', 'tojson', 'topn',
                    'topnperlevel', 'topnskip', 'totalmtd', 'totalqtd', 'totalytd',
                    'treatas', 'trim', 'true', 'trunc', 'unichar', 'unicode', 'union',
                    'upper', 'userculture', 'userelationship', 'username', 'userobjectid',
                    'userprincipalname', 'utcnow', 'utctoday', 'value', 'values', 'var.p',
                    'var.s', 'varx.p', 'varx.s', 'vdb', 'weekday', 'weeknum', 'window',
                    'xirr', 'xnpv', 'year', 'yearfrac', 'yield', 'yielddisc', 'yieldmat'),
                 prefix=r'(?i)', suffix=r'\b'), Name.Function), #Functions

            (words(('at','asc','boolean','both','by','create','currency',
                'datetime','day','define','desc','double',
                'evaluate','false','integer','measure',
                'month','none','order','return','single','start','string',
                'table','true','var','year'),
                prefix=r'(?i)', suffix=r'\b'), Name.Builtin), # Keyword

            (r':=|[-+*\/=^]', Operator),
            (r'\b(IN|NOT)\b', Operator.Word),
            (r'"', String, 'string'), #StringLiteral
            (r"'(?:[^']|'')*'(?!')(?:\[[ \w]+\])?|\w+\[[ \w]+\]",
                Name.Attribute),	# Column reference
            (r"\[[ \w]+\]", Name.Attribute), #Measure reference
            (r'(?<!\w)(\d+\.?\d*|\.\d+\b)', Number),# Number
            (r'[\[\](){}`,.]', Punctuation), #Parenthesis
            (r'.*\n', Text),

        ],
        'multiline-comments': [
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^/*]+', Comment.Multiline),
            (r'[/*]', Comment.Multiline)
        ],
        'string': [
            (r'""', String.Escape),
            (r'"', String, '#pop'),
            (r'[^"]+', String),
        ]
    }
```
