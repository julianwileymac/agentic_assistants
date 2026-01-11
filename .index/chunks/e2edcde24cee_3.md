# Chunk: e2edcde24cee_3

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rebol.py`
- lines: 166-262
- chunk: 4/7

```
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

    def analyse_text(text):
        """
        Check if code contains REBOL header and so it probably not R code
        """
        if re.match(r'^\s*REBOL\s*\[', text, re.IGNORECASE):
            # The code starts with REBOL header
            return 1.0
        elif re.search(r'\s*REBOL\s*\[', text, re.IGNORECASE):
            # The code contains REBOL header but also some text before it
            return 0.5


class RedLexer(RegexLexer):
    """
    A Red-language lexer.
    """
    name = 'Red'
    aliases = ['red', 'red/system']
    filenames = ['*.red', '*.reds']
    mimetypes = ['text/x-red', 'text/x-red-system']
    url = 'https://www.red-lang.org'
    version_added = '2.0'

    flags = re.IGNORECASE | re.MULTILINE

    escape_re = r'(?:\^\([0-9a-f]{1,4}\)*)'

    def word_callback(lexer, match):
        word = match.group()

        if re.match(".*:$", word):
            yield match.start(), Generic.Subheading, word
        elif re.match(r'(if|unless|either|any|all|while|until|loop|repeat|'
```
