# Chunk: 7e6f1b19fdab_1

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 81-161
- chunk: 2/8

```
"Eliminate all spacing between prompts.")
shell_flags['pylab'] = (
    {'InteractiveShellApp' : {'pylab' : 'auto'}},
    """Pre-load matplotlib and numpy for interactive use with
    the default matplotlib backend. The exact options available
    depend on what Matplotlib provides at runtime.""",
)
shell_flags['matplotlib'] = (
    {'InteractiveShellApp' : {'matplotlib' : 'auto'}},
    """Configure matplotlib for interactive use with
    the default matplotlib backend. The exact options available
    depend on what Matplotlib provides at runtime.""",
)

# it's possible we don't want short aliases for *all* of these:
shell_aliases = dict(
    autocall="InteractiveShell.autocall",
    colors="InteractiveShell.colors",
    theme="InteractiveShell.colors",
    logfile="InteractiveShell.logfile",
    logappend="InteractiveShell.logappend",
    c="InteractiveShellApp.code_to_run",
    m="InteractiveShellApp.module_to_run",
    ext="InteractiveShellApp.extra_extensions",
    gui='InteractiveShellApp.gui',
    pylab='InteractiveShellApp.pylab',
    matplotlib='InteractiveShellApp.matplotlib',
)
shell_aliases['cache-size'] = 'InteractiveShell.cache_size'


# -----------------------------------------------------------------------------
# Traitlets
# -----------------------------------------------------------------------------


class MatplotlibBackendCaselessStrEnum(CaselessStrEnum):
    """An enum of Matplotlib backend strings where the case should be ignored.

    Prior to Matplotlib 3.9.0 the list of valid backends is hardcoded in
    pylabtools.backends. After that, Matplotlib manages backends.

    The list of valid backends is determined when it is first needed to avoid
    wasting unnecessary initialisation time.
    """

    def __init__(
        self: CaselessStrEnum[t.Any],
        default_value: t.Any = Undefined,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(None, default_value=default_value, **kwargs)

    def __getattribute__(self, name):
        if name == "values" and object.__getattribute__(self, name) is None:
            from IPython.core.pylabtools import _list_matplotlib_backends_and_gui_loops

            self.values = _list_matplotlib_backends_and_gui_loops()
        return object.__getattribute__(self, name)


#-----------------------------------------------------------------------------
# Main classes and functions
#-----------------------------------------------------------------------------

class InteractiveShellApp(Configurable):
    """A Mixin for applications that start InteractiveShell instances.

    Provides configurables for loading extensions and executing files
    as part of configuring a Shell environment.

    The following methods should be called by the :meth:`initialize` method
    of the subclass:

      - :meth:`init_path`
      - :meth:`init_shell` (to be implemented by the subclass)
      - :meth:`init_gui_pylab`
      - :meth:`init_extensions`
      - :meth:`init_code`
    """
```
