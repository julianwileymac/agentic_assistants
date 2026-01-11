# Chunk: 8ade7dbb48a6_3

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 241-325
- chunk: 4/11

```
 = arg
        elif isinstance(arg, str):
            # Decorator called with arguments (@foo('bar'))
            name = arg

            def mark(func, *a, **kw):
                ip.register_magic_function(func, magic_kind, name)
                return func

            retval = mark
        else:
            raise TypeError("Decorator can only be called with string or function")
        return retval

    # Ensure the resulting decorator has a usable docstring
    ds = _docstring_template.format("function", magic_kind)

    ds += dedent(
        """
    Note: this decorator can only be used in a context where IPython is already
    active, so that the `get_ipython()` call succeeds.  You can therefore use
    it in your startup files loaded after IPython initializes, but *not* in the
    IPython configuration file itself, which is executed before IPython is
    fully up and running.  Any file located in the `startup` subdirectory of
    your configuration profile will be OK in this sense.
    """
    )

    magic_deco.__doc__ = ds
    return magic_deco


MAGIC_NO_VAR_EXPAND_ATTR = "_ipython_magic_no_var_expand"
MAGIC_OUTPUT_CAN_BE_SILENCED = "_ipython_magic_output_can_be_silenced"


def no_var_expand(magic_func):
    """Mark a magic function as not needing variable expansion

    By default, IPython interprets `{a}` or `$a` in the line passed to magics
    as variables that should be interpolated from the interactive namespace
    before passing the line to the magic function.
    This is not always desirable, e.g. when the magic executes Python code
    (%timeit, %time, etc.).
    Decorate magics with `@no_var_expand` to opt-out of variable expansion.

    .. versionadded:: 7.3
    """
    setattr(magic_func, MAGIC_NO_VAR_EXPAND_ATTR, True)
    return magic_func


def output_can_be_silenced(magic_func):
    """Mark a magic function so its output may be silenced.

    The output is silenced if the Python code used as a parameter of
    the magic ends in a semicolon, not counting a Python comment that can
    follow it.
    """
    setattr(magic_func, MAGIC_OUTPUT_CAN_BE_SILENCED, True)
    return magic_func


# Create the actual decorators for public use

# These three are used to decorate methods in class definitions
line_magic = _method_magic_marker("line")
cell_magic = _method_magic_marker("cell")
line_cell_magic = _method_magic_marker("line_cell")

# These three decorate standalone functions and perform the decoration
# immediately.  They can only run where get_ipython() works
register_line_magic = _function_magic_marker("line")
register_cell_magic = _function_magic_marker("cell")
register_line_cell_magic = _function_magic_marker("line_cell")

# -----------------------------------------------------------------------------
# Core Magic classes
# -----------------------------------------------------------------------------


class MagicsManager(Configurable):
    """Object that handles all magic-related functionality for IPython."""
```
