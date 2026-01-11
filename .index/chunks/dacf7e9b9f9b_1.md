# Chunk: dacf7e9b9f9b_1

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/install_lib.py`
- lines: 72-159
- chunk: 2/4

```
dir'),
            ('force', 'force'),
            ('compile', 'compile'),
            ('optimize', 'optimize'),
            ('skip_build', 'skip_build'),
        )

        if self.compile is None:
            self.compile = True
        if self.optimize is None:
            self.optimize = False

        if not isinstance(self.optimize, int):
            try:
                self.optimize = int(self.optimize)
            except ValueError:
                pass
            if self.optimize not in (0, 1, 2):
                raise DistutilsOptionError("optimize must be 0, 1, or 2")

    def run(self) -> None:
        # Make sure we have built everything we need first
        self.build()

        # Install everything: simply dump the entire contents of the build
        # directory to the installation directory (that's the beauty of
        # having a build directory!)
        outfiles = self.install()

        # (Optionally) compile .py to .pyc
        if outfiles is not None and self.distribution.has_pure_modules():
            self.byte_compile(outfiles)

    # -- Top-level worker functions ------------------------------------
    # (called from 'run()')

    def build(self) -> None:
        if not self.skip_build:
            if self.distribution.has_pure_modules():
                self.run_command('build_py')
            if self.distribution.has_ext_modules():
                self.run_command('build_ext')

    # Any: https://typing.readthedocs.io/en/latest/guides/writing_stubs.html#the-any-trick
    def install(self) -> list[str] | Any:
        if os.path.isdir(self.build_dir):
            outfiles = self.copy_tree(self.build_dir, self.install_dir)
        else:
            self.warn(
                f"'{self.build_dir}' does not exist -- no Python modules to install"
            )
            return
        return outfiles

    def byte_compile(self, files) -> None:
        if sys.dont_write_bytecode:
            self.warn('byte-compiling is disabled, skipping.')
            return

        from ..util import byte_compile

        # Get the "--root" directory supplied to the "install" command,
        # and use it as a prefix to strip off the purported filename
        # encoded in bytecode files.  This is far from complete, but it
        # should at least generate usable bytecode in RPM distributions.
        install_root = self.get_finalized_command('install').root

        if self.compile:
            byte_compile(
                files,
                optimize=0,
                force=self.force,
                prefix=install_root,
                dry_run=self.dry_run,
            )
        if self.optimize > 0:
            byte_compile(
                files,
                optimize=self.optimize,
                force=self.force,
                prefix=install_root,
                verbose=self.verbose,
                dry_run=self.dry_run,
            )

    # -- Utility methods -----------------------------------------------
```
