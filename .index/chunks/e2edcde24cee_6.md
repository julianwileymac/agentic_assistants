# Chunk: e2edcde24cee_6

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rebol.py`
- lines: 347-420
- chunk: 7/7

```
(^{")\s]+)', Text),
        ],
        'string': [
            (r'[^(^")]+', String),
            (escape_re, String.Escape),
            (r'[(|)]+', String),
            (r'\^.', String.Escape),
            (r'"', String, '#pop'),
        ],
        'string2': [
            (r'[^(^{})]+', String),
            (escape_re, String.Escape),
            (r'[(|)]+', String),
            (r'\^.', String.Escape),
            (r'\{', String, '#push'),
            (r'\}', String, '#pop'),
        ],
        'stringFile': [
            (r'[^(^")]+', Name.Decorator),
            (escape_re, Name.Decorator),
            (r'\^.', Name.Decorator),
            (r'"', Name.Decorator, '#pop'),
        ],
        'char': [
            (escape_re + '"', String.Char, '#pop'),
            (r'\^."', String.Char, '#pop'),
            (r'."', String.Char, '#pop'),
        ],
        'tag': [
            (escape_re, Name.Tag),
            (r'"', Name.Tag, 'tagString'),
            (r'[^(<>\r\n")]+', Name.Tag),
            (r'>', Name.Tag, '#pop'),
        ],
        'tagString': [
            (r'[^(^")]+', Name.Tag),
            (escape_re, Name.Tag),
            (r'[(|)]+', Name.Tag),
            (r'\^.', Name.Tag),
            (r'"', Name.Tag, '#pop'),
        ],
        'tuple': [
            (r'(\d+\.)+', Keyword.Constant),
            (r'\d+', Keyword.Constant, '#pop'),
        ],
        'bin2': [
            (r'\s+', Number.Hex),
            (r'([01]\s*){8}', Number.Hex),
            (r'\}', Number.Hex, '#pop'),
        ],
        'commentString1': [
            (r'[^(^")]+', Comment),
            (escape_re, Comment),
            (r'[(|)]+', Comment),
            (r'\^.', Comment),
            (r'"', Comment, '#pop'),
        ],
        'commentString2': [
            (r'[^(^{})]+', Comment),
            (escape_re, Comment),
            (r'[(|)]+', Comment),
            (r'\^.', Comment),
            (r'\{', Comment, '#push'),
            (r'\}', Comment, '#pop'),
        ],
        'commentBlock': [
            (r'\[', Comment, '#push'),
            (r'\]', Comment, '#pop'),
            (r'"', Comment, "commentString1"),
            (r'\{', Comment, "commentString2"),
            (r'[^(\[\]"{)]+', Comment),
        ],
    }
```
