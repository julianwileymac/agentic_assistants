# Chunk: cebaecbbd1d7_11

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 743-803
- chunk: 12/13

```
 + name

        initfunc_name = "PyInit" + suffix
        if initfunc_name not in ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        return ext.export_symbols

    def _get_module_name_for_symbol(self, ext):
        # Package name should be used for `__init__` modules
        # https://github.com/python/cpython/issues/80074
        # https://github.com/pypa/setuptools/issues/4826
        parts = ext.name.split(".")
        if parts[-1] == "__init__" and len(parts) >= 2:
            return parts[-2]
        return parts[-1]

    def get_libraries(self, ext: Extension) -> list[str]:  # noqa: C901
        """Return the list of libraries to link against when building a
        shared extension.  On most platforms, this is just 'ext.libraries';
        on Windows, we add the Python library (eg. python20.dll).
        """
        # The python library is always needed on Windows.  For MSVC, this
        # is redundant, since the library is mentioned in a pragma in
        # pyconfig.h that MSVC groks.  The other Windows compilers all seem
        # to need it mentioned explicitly, though, so that's what we do.
        # Append '_d' to the python import library on debug builds.
        if sys.platform == "win32" and not is_mingw():
            from .._msvccompiler import MSVCCompiler

            if not isinstance(self.compiler, MSVCCompiler):
                template = "python%d%d"
                if self.debug:
                    template = template + '_d'
                pythonlib = template % (
                    sys.hexversion >> 24,
                    (sys.hexversion >> 16) & 0xFF,
                )
                # don't extend ext.libraries, it may be shared with other
                # extensions, it is a reference to the original list
                return ext.libraries + [pythonlib]
        else:
            # On Android only the main executable and LD_PRELOADs are considered
            # to be RTLD_GLOBAL, all the dependencies of the main executable
            # remain RTLD_LOCAL and so the shared libraries must be linked with
            # libpython when python is built with a shared python library (issue
            # bpo-21536).
            # On Cygwin (and if required, other POSIX-like platforms based on
            # Windows like MinGW) it is simply necessary that all symbols in
            # shared libraries are resolved at link time.
            from ..sysconfig import get_config_var

            link_libpython = False
            if get_config_var('Py_ENABLE_SHARED'):
                # A native build on an Android device or on Cygwin
                if hasattr(sys, 'getandroidapilevel'):
                    link_libpython = True
                elif sys.platform == 'cygwin' or is_mingw():
                    link_libpython = True
                elif '_PYTHON_HOST_PLATFORM' in os.environ:
                    # We are cross-compiling for one of the relevant platforms
```
