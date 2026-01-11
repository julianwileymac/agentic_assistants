# Chunk: 8ade7dbb48a6_2

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 159-252
- chunk: 3/11

```
ts: it will create a {1} magic named as the {0} being
decorated::

    @deco
    def foo(...)

will create a {1} magic named `foo`.

ii) with one string argument: which will be used as the actual name of the
resulting magic::

    @deco('bar')
    def foo(...)

will create a {1} magic named `bar`.

To register a class magic use ``Interactiveshell.register_magic(class or instance)``.
"""

# These two are decorator factories.  While they are conceptually very similar,
# there are enough differences in the details that it's simpler to have them
# written as completely standalone functions rather than trying to share code
# and make a single one with convoluted logic.


def _method_magic_marker(magic_kind):
    """Decorator factory for methods in Magics subclasses."""

    validate_type(magic_kind)

    # This is a closure to capture the magic_kind.  We could also use a class,
    # but it's overkill for just that one bit of state.
    def magic_deco(arg):
        if callable(arg):
            # "Naked" decorator call (just @foo, no args)
            func = arg
            name = func.__name__
            retval = arg
            record_magic(magics, magic_kind, name, name)
        elif isinstance(arg, str):
            # Decorator called with arguments (@foo('bar'))
            name = arg

            def mark(func, *a, **kw):
                record_magic(magics, magic_kind, name, func.__name__)
                return func

            retval = mark
        else:
            raise TypeError("Decorator can only be called with string or function")
        return retval

    # Ensure the resulting decorator has a usable docstring
    magic_deco.__doc__ = _docstring_template.format("method", magic_kind)
    return magic_deco


def _function_magic_marker(magic_kind):
    """Decorator factory for standalone functions."""
    validate_type(magic_kind)

    # This is a closure to capture the magic_kind.  We could also use a class,
    # but it's overkill for just that one bit of state.
    def magic_deco(arg):
        # Find get_ipython() in the caller's namespace
        caller = sys._getframe(1)
        for ns in ["f_locals", "f_globals", "f_builtins"]:
            get_ipython = getattr(caller, ns).get("get_ipython")
            if get_ipython is not None:
                break
        else:
            raise NameError(
                "Decorator can only run in context where `get_ipython` exists"
            )

        ip = get_ipython()

        if callable(arg):
            # "Naked" decorator call (just @foo, no args)
            func = arg
            name = func.__name__
            ip.register_magic_function(func, magic_kind, name)
            retval = arg
        elif isinstance(arg, str):
            # Decorator called with arguments (@foo('bar'))
            name = arg

            def mark(func, *a, **kw):
                ip.register_magic_function(func, magic_kind, name)
                return func

            retval = mark
        else:
```
