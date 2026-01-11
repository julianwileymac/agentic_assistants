# Chunk: b9ed8f9aa0ca_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/smalltalk.py`
- lines: 141-195
- chunk: 3/3

```
 For Newspeak syntax.
    """
    name = 'Newspeak'
    url = 'http://newspeaklanguage.org/'
    filenames = ['*.ns2']
    aliases = ['newspeak', ]
    mimetypes = ['text/x-newspeak']
    version_added = '1.1'

    tokens = {
        'root': [
            (r'\b(Newsqueak2)\b', Keyword.Declaration),
            (r"'[^']*'", String),
            (r'\b(class)(\s+)(\w+)(\s*)',
             bygroups(Keyword.Declaration, Text, Name.Class, Text)),
            (r'\b(mixin|self|super|private|public|protected|nil|true|false)\b',
             Keyword),
            (r'(\w+\:)(\s*)([a-zA-Z_]\w+)',
             bygroups(Name.Function, Text, Name.Variable)),
            (r'(\w+)(\s*)(=)',
             bygroups(Name.Attribute, Text, Operator)),
            (r'<\w+>', Comment.Special),
            include('expressionstat'),
            include('whitespace')
        ],

        'expressionstat': [
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'\d+', Number.Integer),
            (r':\w+', Name.Variable),
            (r'(\w+)(::)', bygroups(Name.Variable, Operator)),
            (r'\w+:', Name.Function),
            (r'\w+', Name.Variable),
            (r'\(|\)', Punctuation),
            (r'\[|\]', Punctuation),
            (r'\{|\}', Punctuation),

            (r'(\^|\+|\/|~|\*|<|>|=|@|%|\||&|\?|!|,|-|:)', Operator),
            (r'\.|;', Punctuation),
            include('whitespace'),
            include('literals'),
        ],
        'literals': [
            (r'\$.', String),
            (r"'[^']*'", String),
            (r"#'[^']*'", String.Symbol),
            (r"#\w+:?", String.Symbol),
            (r"#(\+|\/|~|\*|<|>|=|@|%|\||&|\?|!|,|-)+", String.Symbol)
        ],
        'whitespace': [
            (r'\s+', Text),
            (r'"[^"]*"', Comment)
        ],
    }
```
