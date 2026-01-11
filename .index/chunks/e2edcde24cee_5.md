# Chunk: e2edcde24cee_5

- source: `.venv-lab/Lib/site-packages/pygments/lexers/rebol.py`
- lines: 294-358
- chunk: 6/7

```
re.match(r'(\+|-\*\*|-|\*\*|//|/|\*|and|or|xor|=\?|===|==|=|<>|<=|>=|'
                      r'<<<|>>>|<<|>>|<|>%)$', word):
            yield match.start(), Operator, word
        elif re.match(r".*\!$", word):
            yield match.start(), Keyword.Type, word
        elif re.match("'.*", word):
            yield match.start(), Name.Variable.Instance, word  # lit-word
        elif re.match("#.*", word):
            yield match.start(), Name.Label, word  # issue
        elif re.match("%.*", word):
            yield match.start(), Name.Decorator, word  # file
        elif re.match(":.*", word):
            yield match.start(), Generic.Subheading, word  # get-word
        else:
            yield match.start(), Name.Variable, word

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'#"', String.Char, 'char'),
            (r'#\{[0-9a-f\s]*\}', Number.Hex),
            (r'2#\{', Number.Hex, 'bin2'),
            (r'64#\{[0-9a-z+/=\s]*\}', Number.Hex),
            (r'([0-9a-f]+)(h)((\s)|(?=[\[\]{}"()]))',
             bygroups(Number.Hex, Name.Variable, Whitespace)),
            (r'"', String, 'string'),
            (r'\{', String, 'string2'),
            (r';#+.*\n', Comment.Special),
            (r';\*+.*\n', Comment.Preproc),
            (r';.*\n', Comment),
            (r'%"', Name.Decorator, 'stringFile'),
            (r'%[^(^{")\s\[\]]+', Name.Decorator),
            (r'[+-]?([a-z]{1,3})?\$\d+(\.\d+)?', Number.Float),  # money
            (r'[+-]?\d+\:\d+(\:\d+)?(\.\d+)?', String.Other),    # time
            (r'\d+[\-/][0-9a-z]+[\-/]\d+(/\d+:\d+((:\d+)?'
             r'([\.\d+]?([+-]?\d+:\d+)?)?)?)?', String.Other),   # date
            (r'\d+(\.\d+)+\.\d+', Keyword.Constant),             # tuple
            (r'\d+X\d+', Keyword.Constant),                   # pair
            (r'[+-]?\d+(\'\d+)?([.,]\d*)?E[+-]?\d+', Number.Float),
            (r'[+-]?\d+(\'\d+)?[.,]\d*', Number.Float),
            (r'[+-]?\d+(\'\d+)?', Number),
            (r'[\[\]()]', Generic.Strong),
            (r'[a-z]+[^(^{"\s:)]*://[^(^{"\s)]*', Name.Decorator),  # url
            (r'mailto:[^(^{"@\s)]+@[^(^{"@\s)]+', Name.Decorator),  # url
            (r'[^(^{"@\s)]+@[^(^{"@\s)]+', Name.Decorator),         # email
            (r'comment\s"', Comment, 'commentString1'),
            (r'comment\s\{', Comment, 'commentString2'),
            (r'comment\s\[', Comment, 'commentBlock'),
            (r'comment\s[^(\s{"\[]+', Comment),
            (r'/[^(^{^")\s/[\]]*', Name.Attribute),
            (r'([^(^{^")\s/[\]]+)(?=[:({"\s/\[\]])', word_callback),
            (r'<[\w:.-]*>', Name.Tag),
            (r'<[^(<>\s")]+', Name.Tag, 'tag'),
            (r'([^(^{")\s]+)', Text),
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
```
