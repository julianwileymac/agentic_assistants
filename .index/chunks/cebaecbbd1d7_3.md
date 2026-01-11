# Chunk: cebaecbbd1d7_3

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/build_ext.py`
- lines: 218-284
- chunk: 4/13

```
or Release and Debug builds.
        # also Python's library directory must be appended to library_dirs
        if os.name == 'nt' and not is_mingw():
            # the 'libs' directory is for binary installs - we assume that
            # must be the *native* platform.  But we don't really support
            # cross-compiling via a binary install anyway, so we let it go.
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            if sys.base_exec_prefix != sys.prefix:  # Issue 16116
                self.library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))
            if self.debug:
                self.build_temp = os.path.join(self.build_temp, "Debug")
            else:
                self.build_temp = os.path.join(self.build_temp, "Release")

            # Append the source distribution include and library directories,
            # this allows distutils on windows to work in the source tree
            self.include_dirs.append(os.path.dirname(get_config_h_filename()))
            self.library_dirs.append(sys.base_exec_prefix)

            # Use the .lib files for the correct architecture
            if self.plat_name == 'win32':
                suffix = 'win32'
            else:
                # win-amd64
                suffix = self.plat_name[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            if suffix:
                new_lib = os.path.join(new_lib, suffix)
            self.library_dirs.append(new_lib)

        # For extensions under Cygwin, Python's library directory must be
        # appended to library_dirs
        if sys.platform[:6] == 'cygwin':
            if not sysconfig.python_build:
                # building third party extensions
                self.library_dirs.append(
                    os.path.join(
                        sys.prefix, "lib", "python" + get_python_version(), "config"
                    )
                )
            else:
                # building python standard extensions
                self.library_dirs.append('.')

        self.library_dirs.extend(self._python_lib_dir(sysconfig))

        # The argument parsing will result in self.define being a string, but
        # it has to be a list of 2-tuples.  All the preprocessor symbols
        # specified by the 'define' option will be set to '1'.  Multiple
        # symbols can be separated with commas.

        if self.define:
            defines = self.define.split(',')
            self.define = [(symbol, '1') for symbol in defines]

        # The option for macros to undefine is also a string from the
        # option parsing, but has to be a list.  Multiple symbols can also
        # be separated with commas here.
        if self.undef:
            self.undef = self.undef.split(',')

        if self.swig_opts is None:
            self.swig_opts = []
        else:
            self.swig_opts = self.swig_opts.split(' ')
```
