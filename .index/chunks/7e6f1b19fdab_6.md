# Chunk: 7e6f1b19fdab_6

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 417-491
- chunk: 7/8

```
 + [
            os.path.join(p, 'startup') for p in chain(ENV_CONFIG_DIRS, SYSTEM_CONFIG_DIRS)
        ]
        startup_files = []

        if self.exec_PYTHONSTARTUP and os.environ.get('PYTHONSTARTUP', False) and \
                not (self.file_to_run or self.code_to_run or self.module_to_run):
            python_startup = os.environ['PYTHONSTARTUP']
            self.log.debug("Running PYTHONSTARTUP file %s...", python_startup)
            try:
                self._exec_file(python_startup)
            except:
                self.log.warning("Unknown error in handling PYTHONSTARTUP file %s:", python_startup)
                self.shell.showtraceback()
        for startup_dir in startup_dirs[::-1]:
            startup_files += glob.glob(os.path.join(startup_dir, '*.py'))
            startup_files += glob.glob(os.path.join(startup_dir, '*.ipy'))
        if not startup_files:
            return

        self.log.debug("Running startup files from %s...", startup_dir)
        try:
            for fname in sorted(startup_files):
                self._exec_file(fname)
        except:
            self.log.warning("Unknown error in handling startup files:")
            self.shell.showtraceback()

    def _run_exec_files(self):
        """Run files from IPythonApp.exec_files"""
        if not self.exec_files:
            return

        self.log.debug("Running files in IPythonApp.exec_files...")
        try:
            for fname in self.exec_files:
                self._exec_file(fname)
        except:
            self.log.warning("Unknown error in handling IPythonApp.exec_files:")
            self.shell.showtraceback()

    def _run_cmd_line_code(self):
        """Run code or file specified at the command-line"""
        if self.code_to_run:
            line = self.code_to_run
            try:
                self.log.info("Running code given at command line (c=): %s" %
                              line)
                self.shell.run_cell(line, store_history=False)
            except:
                self.log.warning("Error in executing line in user namespace: %s" %
                              line)
                self.shell.showtraceback()
                if not self.interact:
                    self.exit(1)

        # Like Python itself, ignore the second if the first of these is present
        elif self.file_to_run:
            fname = self.file_to_run
            if os.path.isdir(fname):
                fname = os.path.join(fname, "__main__.py")
            if not os.path.exists(fname):
                self.log.warning("File '%s' doesn't exist", fname)
                if not self.interact:
                    self.exit(2)
            try:
                self._exec_file(fname, shell_futures=True)
            except:
                self.shell.showtraceback(tb_offset=4)
                if not self.interact:
                    self.exit(1)

    def _run_module(self):
        """Run module specified at the command-line."""
```
