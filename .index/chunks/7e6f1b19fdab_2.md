# Chunk: 7e6f1b19fdab_2

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 150-229
- chunk: 3/8

```
l environment.

    The following methods should be called by the :meth:`initialize` method
    of the subclass:

      - :meth:`init_path`
      - :meth:`init_shell` (to be implemented by the subclass)
      - :meth:`init_gui_pylab`
      - :meth:`init_extensions`
      - :meth:`init_code`
    """
    extensions = List(Unicode(),
        help="A list of dotted module names of IPython extensions to load."
    ).tag(config=True)

    extra_extensions = List(
        DottedObjectName(),
        help="""
        Dotted module name(s) of one or more IPython extensions to load.

        For specifying extra extensions to load on the command-line.

        .. versionadded:: 7.10
        """,
    ).tag(config=True)

    reraise_ipython_extension_failures = Bool(False,
        help="Reraise exceptions encountered loading IPython extensions?",
    ).tag(config=True)

    # Extensions that are always loaded (not configurable)
    default_extensions = List(Unicode(), [u'storemagic']).tag(config=False)

    hide_initial_ns = Bool(True,
        help="""Should variables loaded at startup (by startup files, exec_lines, etc.)
        be hidden from tools like %who?"""
    ).tag(config=True)

    exec_files = List(Unicode(),
        help="""List of files to run at IPython startup."""
    ).tag(config=True)
    exec_PYTHONSTARTUP = Bool(True,
        help="""Run the file referenced by the PYTHONSTARTUP environment
        variable at IPython startup."""
    ).tag(config=True)
    file_to_run = Unicode('',
        help="""A file to be run""").tag(config=True)

    exec_lines = List(Unicode(),
        help="""lines of code to run at IPython startup."""
    ).tag(config=True)
    code_to_run = Unicode("", help="Execute the given command string.").tag(config=True)
    module_to_run = Unicode("", help="Run the module as a script.").tag(config=True)
    gui = CaselessStrEnum(
        gui_keys,
        allow_none=True,
        help="Enable GUI event loop integration with any of {0}.".format(gui_keys),
    ).tag(config=True)
    matplotlib = MatplotlibBackendCaselessStrEnum(
        allow_none=True,
        help="""Configure matplotlib for interactive use with
        the default matplotlib backend. The exact options available
        depend on what Matplotlib provides at runtime.""",
    ).tag(config=True)
    pylab = MatplotlibBackendCaselessStrEnum(
        allow_none=True,
        help="""Pre-load matplotlib and numpy for interactive use,
        selecting a particular matplotlib backend and loop integration.
        The exact options available depend on what Matplotlib provides at runtime.
        """,
    ).tag(config=True)
    pylab_import_all = Bool(
        True,
        help="""If true, IPython will populate the user namespace with numpy, pylab, etc.
        and an ``import *`` is done from numpy and pylab, when using pylab mode.

        When False, pylab mode should not import any names into the user namespace.
        """,
    ).tag(config=True)
```
