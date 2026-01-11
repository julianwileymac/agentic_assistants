# Chunk: 8ade7dbb48a6_1

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 85-175
- chunk: 2/11

```
o run."""
    func.needs_local_scope = True
    return func


# -----------------------------------------------------------------------------
# Class and method decorators for registering magics
# -----------------------------------------------------------------------------


def magics_class(cls):
    """Class decorator for all subclasses of the main Magics class.

    Any class that subclasses Magics *must* also apply this decorator, to
    ensure that all the methods that have been decorated as line/cell magics
    get correctly registered in the class instance.  This is necessary because
    when method decorators run, the class does not exist yet, so they
    temporarily store their information into a module global.  Application of
    this class decorator copies that global data to the class instance and
    clears the global.

    Obviously, this mechanism is not thread-safe, which means that the
    *creation* of subclasses of Magic should only be done in a single-thread
    context.  Instantiation of the classes has no restrictions.  Given that
    these classes are typically created at IPython startup time and before user
    application code becomes active, in practice this should not pose any
    problems.
    """
    cls.registered = True
    cls.magics = dict(line=magics["line"], cell=magics["cell"])
    magics["line"] = {}
    magics["cell"] = {}
    return cls


def record_magic(dct, magic_kind, magic_name, func):
    """Utility function to store a function as a magic of a specific kind.

    Parameters
    ----------
    dct : dict
        A dictionary with 'line' and 'cell' subdicts.
    magic_kind : str
        Kind of magic to be stored.
    magic_name : str
        Key to store the magic as.
    func : function
        Callable object to store.
    """
    if magic_kind == "line_cell":
        dct["line"][magic_name] = dct["cell"][magic_name] = func
    else:
        dct[magic_kind][magic_name] = func


def validate_type(magic_kind):
    """Ensure that the given magic_kind is valid.

    Check that the given magic_kind is one of the accepted spec types (stored
    in the global `magic_spec`), raise ValueError otherwise.
    """
    if magic_kind not in magic_spec:
        raise ValueError(
            "magic_kind must be one of %s, %s given" % magic_kinds, magic_kind
        )


# The docstrings for the decorator below will be fairly similar for the two
# types (method and function), so we generate them here once and reuse the
# templates below.
_docstring_template = """Decorate the given {0} as {1} magic.

The decorator can be used with or without arguments, as follows.

i) without arguments: it will create a {1} magic named as the {0} being
decorated::

    @deco
    def foo(...)

will create a {1} magic named `foo`.

ii) with one string argument: which will be used as the actual name of the
resulting magic::

    @deco('bar')
    def foo(...)

will create a {1} magic named `bar`.
```
