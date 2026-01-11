# Chunk: b86eb5ec4e5a_7

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ruby.py`
- lines: 429-495
- chunk: 8/9

```
 yield match.start(), Generic.Output, line
        if curcode:
            yield from do_insertions(
                insertions, rblexer.get_tokens_unprocessed(curcode))


class FancyLexer(RegexLexer):
    """
    Pygments Lexer For Fancy.

    Fancy is a self-hosted, pure object-oriented, dynamic,
    class-based, concurrent general-purpose programming language
    running on Rubinius, the Ruby VM.
    """
    name = 'Fancy'
    url = 'https://github.com/bakkdoor/fancy'
    filenames = ['*.fy', '*.fancypack']
    aliases = ['fancy', 'fy']
    mimetypes = ['text/x-fancysrc']
    version_added = '1.5'

    tokens = {
        # copied from PerlLexer:
        'balanced-regex': [
            (r'/(\\\\|\\[^\\]|[^/\\])*/[egimosx]*', String.Regex, '#pop'),
            (r'!(\\\\|\\[^\\]|[^!\\])*![egimosx]*', String.Regex, '#pop'),
            (r'\\(\\\\|[^\\])*\\[egimosx]*', String.Regex, '#pop'),
            (r'\{(\\\\|\\[^\\]|[^}\\])*\}[egimosx]*', String.Regex, '#pop'),
            (r'<(\\\\|\\[^\\]|[^>\\])*>[egimosx]*', String.Regex, '#pop'),
            (r'\[(\\\\|\\[^\\]|[^\]\\])*\][egimosx]*', String.Regex, '#pop'),
            (r'\((\\\\|\\[^\\]|[^)\\])*\)[egimosx]*', String.Regex, '#pop'),
            (r'@(\\\\|\\[^\\]|[^@\\])*@[egimosx]*', String.Regex, '#pop'),
            (r'%(\\\\|\\[^\\]|[^%\\])*%[egimosx]*', String.Regex, '#pop'),
            (r'\$(\\\\|\\[^\\]|[^$\\])*\$[egimosx]*', String.Regex, '#pop'),
        ],
        'root': [
            (r'\s+', Whitespace),

            # balanced delimiters (copied from PerlLexer):
            (r's\{(\\\\|\\[^\\]|[^}\\])*\}\s*', String.Regex, 'balanced-regex'),
            (r's<(\\\\|\\[^\\]|[^>\\])*>\s*', String.Regex, 'balanced-regex'),
            (r's\[(\\\\|\\[^\\]|[^\]\\])*\]\s*', String.Regex, 'balanced-regex'),
            (r's\((\\\\|\\[^\\]|[^)\\])*\)\s*', String.Regex, 'balanced-regex'),
            (r'm?/(\\\\|\\[^\\]|[^///\n])*/[gcimosx]*', String.Regex),
            (r'm(?=[/!\\{<\[(@%$])', String.Regex, 'balanced-regex'),

            # Comments
            (r'#(.*?)\n', Comment.Single),
            # Symbols
            (r'\'([^\'\s\[\](){}]+|\[\])', String.Symbol),
            # Multi-line DoubleQuotedString
            (r'"""(\\\\|\\[^\\]|[^\\])*?"""', String),
            # DoubleQuotedString
            (r'"(\\\\|\\[^\\]|[^"\\])*"', String),
            # keywords
            (r'(def|class|try|catch|finally|retry|return|return_local|match|'
             r'case|->|=>)\b', Keyword),
            # constants
            (r'(self|super|nil|false|true)\b', Name.Constant),
            (r'[(){};,/?|:\\]', Punctuation),
            # names
            (words((
                'Object', 'Array', 'Hash', 'Directory', 'File', 'Class', 'String',
                'Number', 'Enumerable', 'FancyEnumerable', 'Block', 'TrueClass',
                'NilClass', 'FalseClass', 'Tuple', 'Symbol', 'Stack', 'Set',
                'FancySpec', 'Method', 'Package', 'Range'), suffix=r'\b'),
```
