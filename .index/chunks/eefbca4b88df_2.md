# Chunk: eefbca4b88df_2

- source: `.venv-lab/Lib/site-packages/nbconvert/filters/highlight.py`
- lines: 168-196
- chunk: 3/3

```
= None
    if language == "ipython2":
        try:
            from IPython.lib.lexers import IPythonLexer
        except ImportError:
            warn("IPython lexer unavailable, falling back on Python", stacklevel=2)
            language = "python"
        else:
            lexer = IPythonLexer()
    elif language == "ipython3":
        try:
            from IPython.lib.lexers import IPython3Lexer
        except ImportError:
            warn("IPython3 lexer unavailable, falling back on Python 3", stacklevel=2)
            language = "python3"
        else:
            lexer = IPython3Lexer()

    if lexer is None:
        try:
            lexer = get_lexer_by_name(language, **lexer_options)
        except ClassNotFound:
            warn("No lexer found for language %r. Treating as plain text." % language, stacklevel=2)
            from pygments.lexers.special import TextLexer

            lexer = TextLexer()

    return highlight(source, lexer, output_formatter)
```
