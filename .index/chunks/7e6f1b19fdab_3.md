# Chunk: 7e6f1b19fdab_3

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 222-301
- chunk: 4/8

```
  True,
        help="""If true, IPython will populate the user namespace with numpy, pylab, etc.
        and an ``import *`` is done from numpy and pylab, when using pylab mode.

        When False, pylab mode should not import any names into the user namespace.
        """,
    ).tag(config=True)
    ignore_cwd = Bool(
        False,
        help="""If True, IPython will not add the current working directory to sys.path.
        When False, the current working directory is added to sys.path, allowing imports
        of modules defined in the current directory."""
    ).tag(config=True)
    shell = Instance('IPython.core.interactiveshell.InteractiveShellABC',
                     allow_none=True)
    # whether interact-loop should start
    interact = Bool(True)

    user_ns = Instance(dict, args=None, allow_none=True)
    @observe('user_ns')
    def _user_ns_changed(self, change):
        if self.shell is not None:
            self.shell.user_ns = change['new']
            self.shell.init_user_ns()

    def init_path(self):
        """Add current working directory, '', to sys.path

        Unless disabled by ignore_cwd config or sys.flags.safe_path.

        Unlike Python's default, we insert before the first `site-packages`
        or `dist-packages` directory,
        so that it is after the standard library.

        .. versionchanged:: 7.2
            Try to insert after the standard library, instead of first.
        .. versionchanged:: 8.0
            Allow optionally not including the current directory in sys.path
        .. versionchanged:: 9.7
            Respect sys.flags.safe_path (PYTHONSAFEPATH and -P flag)
        """
        if "" in sys.path or self.ignore_cwd or sys.flags.safe_path:
            return
        for idx, path in enumerate(sys.path):
            parent, last_part = os.path.split(path)
            if last_part in {'site-packages', 'dist-packages'}:
                break
        else:
            # no site-packages or dist-packages found (?!)
            # back to original behavior of inserting at the front
            idx = 0
        sys.path.insert(idx, '')

    def init_shell(self):
        raise NotImplementedError("Override in subclasses")

    def init_gui_pylab(self):
        """Enable GUI event loop integration, taking pylab into account."""
        enable = False
        shell = self.shell
        if self.pylab:
            enable = lambda key: shell.enable_pylab(key, import_all=self.pylab_import_all)
            key = self.pylab
        elif self.matplotlib:
            enable = shell.enable_matplotlib
            key = self.matplotlib
        elif self.gui:
            enable = shell.enable_gui
            key = self.gui

        if not enable:
            return

        try:
            r = enable(key)
        except ImportError:
            self.log.warning("Eventloop or matplotlib integration failed. Is matplotlib installed?")
            self.shell.showtraceback()
            return
```
