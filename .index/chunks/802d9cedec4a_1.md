# Chunk: 802d9cedec4a_1

- source: `.venv-lab/Lib/site-packages/babel/util.py`
- lines: 92-198
- chunk: 2/4

```

        elif m:
            return m.group(1).decode('latin-1')
        else:
            return None
    finally:
        fp.seek(pos)


PYTHON_FUTURE_IMPORT_re = re.compile(
    r'from\s+__future__\s+import\s+\(*(.+)\)*')


def parse_future_flags(fp: IO[bytes], encoding: str = 'latin-1') -> int:
    """Parse the compiler flags by :mod:`__future__` from the given Python
    code.
    """
    import __future__
    pos = fp.tell()
    fp.seek(0)
    flags = 0
    try:
        body = fp.read().decode(encoding)

        # Fix up the source to be (hopefully) parsable by regexpen.
        # This will likely do untoward things if the source code itself is broken.

        # (1) Fix `import (\n...` to be `import (...`.
        body = re.sub(r'import\s*\([\r\n]+', 'import (', body)
        # (2) Join line-ending commas with the next line.
        body = re.sub(r',\s*[\r\n]+', ', ', body)
        # (3) Remove backslash line continuations.
        body = re.sub(r'\\\s*[\r\n]+', ' ', body)

        for m in PYTHON_FUTURE_IMPORT_re.finditer(body):
            names = [x.strip().strip('()') for x in m.group(1).split(',')]
            for name in names:
                feature = getattr(__future__, name, None)
                if feature:
                    flags |= feature.compiler_flag
    finally:
        fp.seek(pos)
    return flags


def pathmatch(pattern: str, filename: str) -> bool:
    """Extended pathname pattern matching.

    This function is similar to what is provided by the ``fnmatch`` module in
    the Python standard library, but:

     * can match complete (relative or absolute) path names, and not just file
       names, and
     * also supports a convenience pattern ("**") to match files at any
       directory level.

    Examples:

    >>> pathmatch('**.py', 'bar.py')
    True
    >>> pathmatch('**.py', 'foo/bar/baz.py')
    True
    >>> pathmatch('**.py', 'templates/index.html')
    False

    >>> pathmatch('./foo/**.py', 'foo/bar/baz.py')
    True
    >>> pathmatch('./foo/**.py', 'bar/baz.py')
    False

    >>> pathmatch('^foo/**.py', 'foo/bar/baz.py')
    True
    >>> pathmatch('^foo/**.py', 'bar/baz.py')
    False

    >>> pathmatch('**/templates/*.html', 'templates/index.html')
    True
    >>> pathmatch('**/templates/*.html', 'templates/foo/bar.html')
    False

    :param pattern: the glob pattern
    :param filename: the path name of the file to match against
    """
    symbols = {
        '?': '[^/]',
        '?/': '[^/]/',
        '*': '[^/]+',
        '*/': '[^/]+/',
        '**/': '(?:.+/)*?',
        '**': '(?:.+/)*?[^/]+',
    }

    if pattern.startswith('^'):
        buf = ['^']
        pattern = pattern[1:]
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
```
