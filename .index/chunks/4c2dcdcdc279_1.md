# Chunk: 4c2dcdcdc279_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/comal.py`
- lines: 67-82
- chunk: 2/2

```
    (r'"', String, 'string'),
            (_identifier + r":(?=[ \n/])", Name.Label),
            (_identifier + r"[$#]?", Name),
            (r'%[01]+', Number.Bin),
            (r'\$[0-9a-f]+', Number.Hex),
            (r'\d*\.\d*(e[-+]?\d+)?', Number.Float),
            (r'\d+', Number.Integer),
            (r'[(),:;]', Punctuation),
        ],
        'string': [
            (r'[^"]+', String),
            (r'"[0-9]*"', String.Escape),
            (r'"', String, '#pop'),
        ],
    }
```
