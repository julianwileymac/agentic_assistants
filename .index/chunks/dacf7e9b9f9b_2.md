# Chunk: dacf7e9b9f9b_2

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/install_lib.py`
- lines: 148-232
- chunk: 3/4

```

                files,
                optimize=self.optimize,
                force=self.force,
                prefix=install_root,
                verbose=self.verbose,
                dry_run=self.dry_run,
            )

    # -- Utility methods -----------------------------------------------

    def _mutate_outputs(self, has_any, build_cmd, cmd_option, output_dir):
        if not has_any:
            return []

        build_cmd = self.get_finalized_command(build_cmd)
        build_files = build_cmd.get_outputs()
        build_dir = getattr(build_cmd, cmd_option)

        prefix_len = len(build_dir) + len(os.sep)
        outputs = [os.path.join(output_dir, file[prefix_len:]) for file in build_files]

        return outputs

    def _bytecode_filenames(self, py_filenames):
        bytecode_files = []
        for py_file in py_filenames:
            # Since build_py handles package data installation, the
            # list of outputs can contain more than just .py files.
            # Make sure we only report bytecode for the .py files.
            ext = os.path.splitext(os.path.normcase(py_file))[1]
            if ext != PYTHON_SOURCE_EXTENSION:
                continue
            if self.compile:
                bytecode_files.append(
                    importlib.util.cache_from_source(py_file, optimization='')
                )
            if self.optimize > 0:
                bytecode_files.append(
                    importlib.util.cache_from_source(
                        py_file, optimization=self.optimize
                    )
                )

        return bytecode_files

    # -- External interface --------------------------------------------
    # (called by outsiders)

    def get_outputs(self):
        """Return the list of files that would be installed if this command
        were actually run.  Not affected by the "dry-run" flag or whether
        modules have actually been built yet.
        """
        pure_outputs = self._mutate_outputs(
            self.distribution.has_pure_modules(),
            'build_py',
            'build_lib',
            self.install_dir,
        )
        if self.compile:
            bytecode_outputs = self._bytecode_filenames(pure_outputs)
        else:
            bytecode_outputs = []

        ext_outputs = self._mutate_outputs(
            self.distribution.has_ext_modules(),
            'build_ext',
            'build_lib',
            self.install_dir,
        )

        return pure_outputs + bytecode_outputs + ext_outputs

    def get_inputs(self):
        """Get the list of files that are input to this command, ie. the
        files that get installed as they are named in the build tree.
        The files in this list correspond one-to-one to the output
        filenames returned by 'get_outputs()'.
        """
        inputs = []

        if self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
```
