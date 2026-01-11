# Chunk: eefb4afd1899_7

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 327-400
- chunk: 8/13

```
 of a split string."
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.splititer(string, maxsplit, concurrent, timeout)

def findall(pattern, string, flags=0, pos=None, endpos=None, overlapped=False,
  concurrent=None, timeout=None, ignore_unused=False, **kwargs):
    """Return a list of all matches in the string. The matches may be overlapped
    if overlapped is True. If one or more groups are present in the pattern,
    return a list of groups; this will be a list of tuples if the pattern has
    more than one group. Empty matches are included in the result."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.findall(string, pos, endpos, overlapped, concurrent, timeout)

def finditer(pattern, string, flags=0, pos=None, endpos=None, overlapped=False,
  partial=False, concurrent=None, timeout=None, ignore_unused=False, **kwargs):
    """Return an iterator over all matches in the string. The matches may be
    overlapped if overlapped is True. For each match, the iterator returns a
    match object. Empty matches are included in the result."""
    pat = _compile(pattern, flags, ignore_unused, kwargs, True)
    return pat.finditer(string, pos, endpos, overlapped, concurrent, partial,
      timeout)

def compile(pattern, flags=0, ignore_unused=False, cache_pattern=None, **kwargs):
    "Compile a regular expression pattern, returning a pattern object."
    if cache_pattern is None:
        cache_pattern = _cache_all
    return _compile(pattern, flags, ignore_unused, kwargs, cache_pattern)

def purge():
    "Clear the regular expression cache"
    _cache.clear()
    _locale_sensitive.clear()

# Whether to cache all patterns.
_cache_all = True

def cache_all(value=True):
    """Sets whether to cache all patterns, even those are compiled explicitly.
    Passing None has no effect, but returns the current setting."""
    global _cache_all

    if value is None:
        return _cache_all

    _cache_all = value

def template(pattern, flags=0):
    "Compile a template pattern, returning a pattern object."
    return _compile(pattern, flags | TEMPLATE, False, {}, False)

def escape(pattern, special_only=True, literal_spaces=False):
    """Escape a string for use as a literal in a pattern. If special_only is
    True, escape only special characters, else escape all non-alphanumeric
    characters. If literal_spaces is True, don't escape spaces."""
    # Convert it to Unicode.
    if isinstance(pattern, bytes):
        p = pattern.decode("latin-1")
    else:
        p = pattern

    s = []
    if special_only:
        for c in p:
            if c == " " and literal_spaces:
                s.append(c)
            elif c in _METACHARS or c.isspace():
                s.append("\\")
                s.append(c)
            else:
                s.append(c)
    else:
        for c in p:
            if c == " " and literal_spaces:
```
