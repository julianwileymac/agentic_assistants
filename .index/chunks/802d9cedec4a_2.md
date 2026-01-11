# Chunk: 802d9cedec4a_2

- source: `.venv-lab/Lib/site-packages/babel/util.py`
- lines: 186-270
- chunk: 3/4

```
n[1:]
    elif pattern.startswith('./'):
        buf = ['^']
        pattern = pattern[2:]
    else:
        buf = []

    for idx, part in enumerate(re.split('([?*]+/?)', pattern)):
        if idx % 2:
            buf.append(symbols[part])
        elif part:
            buf.append(re.escape(part))
    match = re.match(f"{''.join(buf)}$", filename.replace(os.sep, "/"))
    return match is not None


class TextWrapper(textwrap.TextWrapper):
    wordsep_re = re.compile(
        r'(\s+|'                                  # any whitespace
        r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))',   # em-dash
    )

    # e.g. '\u2068foo bar.py\u2069:42'
    _enclosed_filename_re = re.compile(r'(\u2068[^\u2068]+?\u2069(?::-?\d+)?)')

    def _split(self, text):
        """Splits the text into indivisible chunks while ensuring that file names
        containing spaces are not broken up.
        """
        enclosed_filename_start = '\u2068'
        if enclosed_filename_start not in text:
            # There are no file names which contain spaces, fallback to the default implementation
            return super()._split(text)

        chunks = []
        for chunk in re.split(self._enclosed_filename_re, text):
            if chunk.startswith(enclosed_filename_start):
                chunks.append(chunk)
            else:
                chunks.extend(super()._split(chunk))
        return [c for c in chunks if c]


def wraptext(text: str, width: int = 70, initial_indent: str = '', subsequent_indent: str = '') -> list[str]:
    """Simple wrapper around the ``textwrap.wrap`` function in the standard
    library. This version does not wrap lines on hyphens in words. It also
    does not wrap PO file locations containing spaces.

    :param text: the text to wrap
    :param width: the maximum line width
    :param initial_indent: string that will be prepended to the first line of
                           wrapped output
    :param subsequent_indent: string that will be prepended to all lines save
                              the first of wrapped output
    """
    warnings.warn(
        "`babel.util.wraptext` is deprecated and will be removed in a future version of Babel. "
        "If you need this functionality, use the `babel.util.TextWrapper` class directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    wrapper = TextWrapper(width=width, initial_indent=initial_indent,
                          subsequent_indent=subsequent_indent,
                          break_long_words=False)
    return wrapper.wrap(text)


# TODO (Babel 3.x): Remove this re-export
odict = dict


class FixedOffsetTimezone(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset: float, name: str | None = None) -> None:

        self._offset = datetime.timedelta(minutes=offset)
        if name is None:
            name = 'Etc/GMT%+d' % offset
        self.zone = name

    def __str__(self) -> str:
        return self.zone
```
