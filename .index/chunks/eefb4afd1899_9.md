# Chunk: eefb4afd1899_9

- source: `.venv-lab/Lib/site-packages/regex/_main.py`
- lines: 476-554
- chunk: 10/13

```
wargs = set(kwargs) - {k for k, v in args_needed}
        if unused_kwargs:
            any_one = next(iter(unused_kwargs))
            raise ValueError('unused keyword argument {!a}'.format(any_one))

    if cache_it:
        try:
            # Do we know what keyword arguments are needed?
            args_key = pattern, type(pattern), flags
            args_needed = _named_args[args_key]

            # Are we being provided with its required keyword arguments?
            args_supplied = set()
            if args_needed:
                for k, v in args_needed:
                    try:
                        args_supplied.add((k, frozenset(kwargs[k])))
                    except KeyError:
                        raise error("missing named list: {!r}".format(k))

            complain_unused_args()

            args_supplied = frozenset(args_supplied)

            # Have we already seen this regular expression and named list?
            pattern_key = (pattern, type(pattern), flags, args_supplied,
              DEFAULT_VERSION, pattern_locale)
            return _cache[pattern_key]
        except KeyError:
            # It's a new pattern, or new named list for a known pattern.
            pass

    # Guess the encoding from the class of the pattern string.
    if isinstance(pattern, str):
        guess_encoding = UNICODE
    elif isinstance(pattern, bytes):
        guess_encoding = ASCII
    elif isinstance(pattern, Pattern):
        if flags:
            raise ValueError("cannot process flags argument with a compiled pattern")

        return pattern
    else:
        raise TypeError("first argument must be a string or compiled pattern")

    # Set the default version in the core code in case it has been changed.
    _regex_core.DEFAULT_VERSION = DEFAULT_VERSION

    global_flags = flags

    while True:
        caught_exception = None
        try:
            source = _Source(pattern)
            info = _Info(global_flags, source.char_type, kwargs)
            info.guess_encoding = guess_encoding
            source.ignore_space = bool(info.flags & VERBOSE)
            parsed = _parse_pattern(source, info)
            break
        except _UnscopedFlagSet:
            # Remember the global flags for the next attempt.
            global_flags = info.global_flags
        except error as e:
            caught_exception = e

        if caught_exception:
            raise error(caught_exception.msg, caught_exception.pattern,
              caught_exception.pos)

    if not source.at_end():
        raise error("unbalanced parenthesis", pattern, source.pos)

    # Check the global flags for conflicts.
    version = (info.flags & _ALL_VERSIONS) or DEFAULT_VERSION
    if version not in (0, VERSION0, VERSION1):
        raise ValueError("VERSION0 and VERSION1 flags are mutually incompatible")

    if (info.flags & _ALL_ENCODINGS) not in (0, ASCII, LOCALE, UNICODE):
```
