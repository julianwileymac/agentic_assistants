# Chunk: cebaecbbd1d7_6

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 393-470
- chunk: 7/13

```
e or 2-tuple"
                )

            ext_name, build_info = ext

            log.warning(
                "old-style (ext_name, build_info) tuple found in "
                "ext_modules for extension '%s' "
                "-- please convert to Extension instance",
                ext_name,
            )

            if not (isinstance(ext_name, str) and extension_name_re.match(ext_name)):
                raise DistutilsSetupError(
                    "first element of each tuple in 'ext_modules' "
                    "must be the extension name (a string)"
                )

            if not isinstance(build_info, dict):
                raise DistutilsSetupError(
                    "second element of each tuple in 'ext_modules' "
                    "must be a dictionary (build info)"
                )

            # OK, the (ext_name, build_info) dict is type-safe: convert it
            # to an Extension instance.
            ext = Extension(ext_name, build_info['sources'])

            # Easy stuff: one-to-one mapping from dict elements to
            # instance attributes.
            for key in (
                'include_dirs',
                'library_dirs',
                'libraries',
                'extra_objects',
                'extra_compile_args',
                'extra_link_args',
            ):
                val = build_info.get(key)
                if val is not None:
                    setattr(ext, key, val)

            # Medium-easy stuff: same syntax/semantics, different names.
            ext.runtime_library_dirs = build_info.get('rpath')
            if 'def_file' in build_info:
                log.warning("'def_file' element of build info dict no longer supported")

            # Non-trivial stuff: 'macros' split into 'define_macros'
            # and 'undef_macros'.
            macros = build_info.get('macros')
            if macros:
                ext.define_macros = []
                ext.undef_macros = []
                for macro in macros:
                    if not (isinstance(macro, tuple) and len(macro) in (1, 2)):
                        raise DistutilsSetupError(
                            "'macros' element of build info dict must be 1- or 2-tuple"
                        )
                    if len(macro) == 1:
                        ext.undef_macros.append(macro[0])
                    elif len(macro) == 2:
                        ext.define_macros.append(macro)

            extensions[i] = ext

    def get_source_files(self):
        self.check_extensions_list(self.extensions)
        filenames = []

        # Wouldn't it be neat if we knew the names of header files too...
        for ext in self.extensions:
            filenames.extend(ext.sources)
        return filenames

    def get_outputs(self):
        # Sanity check the 'extensions' list -- can't assume this is being
        # done in the same run as a 'build_extensions()' call (in fact, we
```
