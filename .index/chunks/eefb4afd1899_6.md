# Chunk: eefb4afd1899_6

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 285-333
- chunk: 7/13

```
assed the match object
    and must return a replacement string to be used."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.subf(format, string, count, pos, endpos, concurrent, timeout)

def subn(pattern, repl, string, count=0, flags=0, pos=None, endpos=None,
  concurrent=None, timeout=None, ignore_unused=False, **kwargs):
    """Return a 2-tuple containing (new_string, number). new_string is the string
    obtained by replacing the leftmost (or rightmost with a reverse pattern)
    non-overlapping occurrences of the pattern in the source string by the
    replacement repl. number is the number of substitutions that were made. repl
    can be either a string or a callable; if a string, backslash escapes in it
    are processed; if a callable, it's passed the match object and must return a
    replacement string to be used."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.subn(repl, string, count, pos, endpos, concurrent, timeout)

def subfn(pattern, format, string, count=0, flags=0, pos=None, endpos=None,
  concurrent=None, timeout=None, ignore_unused=False, **kwargs):
    """Return a 2-tuple containing (new_string, number). new_string is the string
    obtained by replacing the leftmost (or rightmost with a reverse pattern)
    non-overlapping occurrences of the pattern in the source string by the
    replacement format. number is the number of substitutions that were made. format
    can be either a string or a callable; if a string, it's treated as a format
    string; if a callable, it's passed the match object and must return a
    replacement string to be used."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.subfn(format, string, count, pos, endpos, concurrent, timeout)

def split(pattern, string, maxsplit=0, flags=0, concurrent=None, timeout=None,
  ignore_unused=False, **kwargs):
    """Split the source string by the occurrences of the pattern, returning a
    list containing the resulting substrings.  If capturing parentheses are used
    in pattern, then the text of all groups in the pattern are also returned as
    part of the resulting list.  If maxsplit is nonzero, at most maxsplit splits
    occur, and the remainder of the string is returned as the final element of
    the list."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.split(string, maxsplit, concurrent, timeout)

def splititer(pattern, string, maxsplit=0, flags=0, concurrent=None,
  timeout=None, ignore_unused=False, **kwargs):
    "Return an iterator yielding the parts of a split string."
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.splititer(string, maxsplit, concurrent, timeout)

def findall(pattern, string, flags=0, pos=None, endpos=None, overlapped=False,
  concurrent=None, timeout=None, ignore_unused=False, **kwargs):
```
