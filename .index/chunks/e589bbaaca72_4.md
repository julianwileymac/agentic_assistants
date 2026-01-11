# Chunk: e589bbaaca72_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py`
- lines: 282-340
- chunk: 5/5

```
open_code(decoded_path) as f:
            code = compile(f.read(), fname, "exec")
    return code, fname


def run_path(path_name, init_globals=None, run_name=None):
    """Execute code located at the specified filesystem location

    Returns the resulting top level namespace dictionary

    The file path may refer directly to a Python script (i.e.
    one that could be directly executed with execfile) or else
    it may refer to a zipfile or directory containing a top
    level __main__.py script.
    """
    if run_name is None:
        run_name = "<run_path>"
    pkg_name = run_name.rpartition(".")[0]
    importer = pkgutil_get_importer(path_name)
    # Trying to avoid importing imp so as to not consume the deprecation warning.
    is_NullImporter = False
    if type(importer).__module__ == "imp":
        if type(importer).__name__ == "NullImporter":
            is_NullImporter = True
    if isinstance(importer, type(None)) or is_NullImporter:
        # Not a valid sys.path entry, so run the code directly
        # execfile() doesn't help as we want to allow compiled files
        code, fname = _get_code_from_file(run_name, path_name)
        return _run_module_code(code, init_globals, run_name, pkg_name=pkg_name, script_name=fname)
    else:
        # Finder is defined for path, so add it to
        # the start of sys.path
        sys.path.insert(0, path_name)
        try:
            # Here's where things are a little different from the run_module
            # case. There, we only had to replace the module in sys while the
            # code was running and doing so was somewhat optional. Here, we
            # have no choice and we have to remove it even while we read the
            # code. If we don't do this, a __loader__ attribute in the
            # existing __main__ module may prevent location of the new module.
            mod_name, mod_spec, code = _get_main_module_details()
            with _TempModule(run_name) as temp_module, _ModifiedArgv0(path_name):
                mod_globals = temp_module.module.__dict__
                return _run_code(code, mod_globals, init_globals, run_name, mod_spec, pkg_name).copy()
        finally:
            try:
                sys.path.remove(path_name)
            except ValueError:
                pass


if __name__ == "__main__":
    # Run the module specified as the next command line argument
    if len(sys.argv) < 2:
        print("No module specified for execution", file=sys.stderr)
    else:
        del sys.argv[0]  # Make the requested module sys.argv[0]
        _run_module_as_main(sys.argv[0])
```
