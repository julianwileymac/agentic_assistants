# Chunk: afb712f6b8ad_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydev_ipython/matplotlibtools.py`
- lines: 81-163
- chunk: 2/3

```
rsion__.split('.')[1])


def is_interactive_backend(backend):
    """Check if backend is interactive"""
    matplotlib = sys.modules["matplotlib"]
    new_api_version = (3, 9)
    installed_version = (
        _get_major_version(matplotlib),
        _get_minor_version(matplotlib)
    )

    if installed_version >= new_api_version:
        interactive_bk = matplotlib.backends.backend_registry.list_builtin(
            matplotlib.backends.BackendFilter.INTERACTIVE)
        non_interactive_bk = matplotlib.backends.backend_registry.list_builtin(
            matplotlib.backends.BackendFilter.NON_INTERACTIVE)
    else:
        from matplotlib.rcsetup import interactive_bk, non_interactive_bk  # @UnresolvedImport

    if backend in interactive_bk:
        return True
    elif backend in non_interactive_bk:
        return False
    else:
        return matplotlib.is_interactive()


def patch_use(enable_gui_function):
    """Patch matplotlib function 'use'"""
    matplotlib = sys.modules["matplotlib"]

    def patched_use(*args, **kwargs):
        matplotlib.real_use(*args, **kwargs)
        gui, backend = find_gui_and_backend()
        enable_gui_function(gui)

    matplotlib.real_use = matplotlib.use
    matplotlib.use = patched_use


def patch_is_interactive():
    """Patch matplotlib function 'use'"""
    matplotlib = sys.modules["matplotlib"]

    def patched_is_interactive():
        return matplotlib.rcParams["interactive"]

    matplotlib.real_is_interactive = matplotlib.is_interactive
    matplotlib.is_interactive = patched_is_interactive


def activate_matplotlib(enable_gui_function):
    """Set interactive to True for interactive backends.
    enable_gui_function - Function which enables gui, should be run in the main thread.
    """
    matplotlib = sys.modules["matplotlib"]
    gui, backend = find_gui_and_backend()
    is_interactive = is_interactive_backend(backend)
    if is_interactive:
        enable_gui_function(gui)
        if not matplotlib.is_interactive():
            sys.stdout.write("Backend %s is interactive backend. Turning interactive mode on.\n" % backend)
        matplotlib.interactive(True)
    else:
        if matplotlib.is_interactive():
            sys.stdout.write("Backend %s is non-interactive backend. Turning interactive mode off.\n" % backend)
        matplotlib.interactive(False)
    patch_use(enable_gui_function)
    patch_is_interactive()


def flag_calls(func):
    """Wrap a function to detect and flag when it gets called.

    This is a decorator which takes a function and wraps it in a function with
    a 'called' attribute. wrapper.called is initialized to False.

    The wrapper.called attribute is set to False right before each call to the
    wrapped function, so if the call fails it remains False.  After the call
    completes, wrapper.called is set to True and the output is returned.

```
