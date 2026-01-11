# Chunk: cebaecbbd1d7_5

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 336-403
- chunk: 6/13

```
nd self.plat_name != get_platform():
            self.compiler.initialize(self.plat_name)

        # The official Windows free threaded Python installer doesn't set
        # Py_GIL_DISABLED because its pyconfig.h is shared with the
        # default build, so define it here (pypa/setuptools#4662).
        if os.name == 'nt' and is_freethreaded():
            self.compiler.define_macro('Py_GIL_DISABLED', '1')

        # And make sure that any compile/link-related options (which might
        # come from the command-line or from the setup script) are set in
        # that CCompiler object -- that way, they automatically apply to
        # all compiling and linking done here.
        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for name, value in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
        if self.libraries is not None:
            self.compiler.set_libraries(self.libraries)
        if self.library_dirs is not None:
            self.compiler.set_library_dirs(self.library_dirs)
        if self.rpath is not None:
            self.compiler.set_runtime_library_dirs(self.rpath)
        if self.link_objects is not None:
            self.compiler.set_link_objects(self.link_objects)

        # Now actually compile and link everything.
        self.build_extensions()

    def check_extensions_list(self, extensions) -> None:  # noqa: C901
        """Ensure that the list of extensions (presumably provided as a
        command option 'extensions') is valid, i.e. it is a list of
        Extension objects.  We also support the old-style list of 2-tuples,
        where the tuples are (ext_name, build_info), which are converted to
        Extension instances here.

        Raise DistutilsSetupError if the structure is invalid anywhere;
        just returns otherwise.
        """
        if not isinstance(extensions, list):
            raise DistutilsSetupError(
                "'ext_modules' option must be a list of Extension instances"
            )

        for i, ext in enumerate(extensions):
            if isinstance(ext, Extension):
                continue  # OK! (assume type-checking done
                # by Extension constructor)

            if not isinstance(ext, tuple) or len(ext) != 2:
                raise DistutilsSetupError(
                    "each element of 'ext_modules' option must be an "
                    "Extension instance or 2-tuple"
                )

            ext_name, build_info = ext

            log.warning(
                "old-style (ext_name, build_info) tuple found in "
                "ext_modules for extension '%s' "
                "-- please convert to Extension instance",
                ext_name,
```
