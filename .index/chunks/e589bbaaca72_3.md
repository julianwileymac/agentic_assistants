# Chunk: e589bbaaca72_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py`
- lines: 206-292
- chunk: 4/5

```
 executed module will have full access to the
    __main__ namespace. If this is not desirable, the run_module()
    function should be used to run the module code in a fresh namespace.

    At the very least, these variables in __main__ will be overwritten:
        __name__
        __file__
        __cached__
        __loader__
        __package__
    """
    try:
        if alter_argv or mod_name != "__main__":  # i.e. -m switch
            mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
        else:  # i.e. directory or zipfile execution
            mod_name, mod_spec, code = _get_main_module_details(_Error)
    except _Error as exc:
        msg = "%s: %s" % (sys.executable, exc)
        sys.exit(msg)
    main_globals = sys.modules["__main__"].__dict__
    if alter_argv:
        sys.argv[0] = mod_spec.origin
    return _run_code(code, main_globals, None, "__main__", mod_spec)


def run_module(mod_name, init_globals=None, run_name=None, alter_sys=False):
    """Execute a module's code without importing it

    Returns the resulting top level namespace dictionary
    """
    mod_name, mod_spec, code = _get_module_details(mod_name)
    if run_name is None:
        run_name = mod_name
    if alter_sys:
        return _run_module_code(code, init_globals, run_name, mod_spec)
    else:
        # Leave the sys module alone
        return _run_code(code, {}, init_globals, run_name, mod_spec)


def _get_main_module_details(error=ImportError):
    # Helper that gives a nicer error message when attempting to
    # execute a zipfile or directory by invoking __main__.py
    # Also moves the standard __main__ out of the way so that the
    # preexisting __loader__ entry doesn't cause issues
    main_name = "__main__"
    saved_main = sys.modules[main_name]
    del sys.modules[main_name]
    try:
        return _get_module_details(main_name)
    except ImportError as exc:
        if main_name in str(exc):
            raise error("can't find %r module in %r" % (main_name, sys.path[0])) from exc
        raise
    finally:
        sys.modules[main_name] = saved_main


try:
    io_open_code = io.open_code
except AttributeError:
    # Compatibility with Python 3.6/3.7
    import tokenize

    io_open_code = tokenize.open


def _get_code_from_file(run_name, fname):
    # Check for a compiled file first
    from pkgutil import read_code

    decoded_path = os.path.abspath(os.fsdecode(fname))
    with io_open_code(decoded_path) as f:
        code = read_code(f)
    if code is None:
        # That didn't work, so try it as normal source code
        with io_open_code(decoded_path) as f:
            code = compile(f.read(), fname, "exec")
    return code, fname


def run_path(path_name, init_globals=None, run_name=None):
    """Execute code located at the specified filesystem location

    Returns the resulting top level namespace dictionary

```
