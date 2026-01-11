# Chunk: eefb4afd1899_8

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 390-484
- chunk: 9/13

```
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
                s.append(c)
            elif c in _ALNUM:
                s.append(c)
            else:
                s.append("\\")
                s.append(c)

    r = "".join(s)
    # Convert it back to bytes if necessary.
    if isinstance(pattern, bytes):
        r = r.encode("latin-1")

    return r

# --------------------------------------------------------------------
# Internals.

from regex import _regex_core
from regex import _regex
from threading import RLock as _RLock
from locale import getpreferredencoding as _getpreferredencoding
from regex._regex_core import *
from regex._regex_core import (_ALL_VERSIONS, _ALL_ENCODINGS, _FirstSetError,
  _UnscopedFlagSet, _check_group_features, _compile_firstset,
  _compile_replacement, _flatten_code, _fold_case, _get_required_string,
  _parse_pattern, _shrink_cache)
from regex._regex_core import (ALNUM as _ALNUM, Info as _Info, OP as _OP, Source
  as _Source, Fuzzy as _Fuzzy)

# Version 0 is the old behaviour, compatible with the original 're' module.
# Version 1 is the new behaviour, which differs slightly.

DEFAULT_VERSION = RegexFlag.VERSION0

_METACHARS = frozenset("()[]{}?*+|^$\\.-#&~")

_regex_core.DEFAULT_VERSION = DEFAULT_VERSION

# Caches for the patterns and replacements.
_cache = {}
_cache_lock = _RLock()
_named_args = {}
_replacement_cache = {}
_locale_sensitive = {}

# Maximum size of the cache.
_MAXCACHE = 500
_MAXREPCACHE = 500

def _compile(pattern, flags, ignore_unused, kwargs, cache_it):
    "Compiles a regular expression to a PatternObject."

    global DEFAULT_VERSION
    try:
        from regex import DEFAULT_VERSION
    except ImportError:
        pass

    # We won't bother to cache the pattern if we're debugging.
    if (flags & DEBUG) != 0:
        cache_it = False

    # What locale is this pattern using?
    locale_key = (type(pattern), pattern)
    if _locale_sensitive.get(locale_key, True) or (flags & LOCALE) != 0:
        # This pattern is, or might be, locale-sensitive.
        pattern_locale = _getpreferredencoding()
    else:
        # This pattern is definitely not locale-sensitive.
        pattern_locale = None

    def complain_unused_args():
        if ignore_unused:
            return

        # Complain about any unused keyword arguments, possibly resulting from a typo.
        unused_kwargs = set(kwargs) - {k for k, v in args_needed}
        if unused_kwargs:
            any_one = next(iter(unused_kwargs))
            raise ValueError('unused keyword argument {!a}'.format(any_one))

    if cache_it:
        try:
            # Do we know what keyword arguments are needed?
```
