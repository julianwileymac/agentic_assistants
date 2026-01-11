# Chunk: 7e6f1b19fdab_5

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 359-424
- chunk: 6/8

```
()

        # flush output, so itwon't be attached to the first cell
        sys.stdout.flush()
        sys.stderr.flush()
        self.shell._sys_modules_keys = set(sys.modules.keys())

    def _run_exec_lines(self):
        """Run lines of code in IPythonApp.exec_lines in the user's namespace."""
        if not self.exec_lines:
            return
        try:
            self.log.debug("Running code from IPythonApp.exec_lines...")
            for line in self.exec_lines:
                try:
                    self.log.info("Running code in user namespace: %s" %
                                  line)
                    self.shell.run_cell(line, store_history=False)
                except:
                    self.log.warning("Error in executing line in user "
                                  "namespace: %s" % line)
                    self.shell.showtraceback()
        except:
            self.log.warning("Unknown error in handling IPythonApp.exec_lines:")
            self.shell.showtraceback()

    def _exec_file(self, fname, shell_futures=False):
        try:
            full_filename = filefind(fname, [u'.', self.ipython_dir])
        except IOError:
            self.log.warning("File not found: %r"%fname)
            return
        # Make sure that the running script gets a proper sys.argv as if it
        # were run from a system shell.
        save_argv = sys.argv
        sys.argv = [full_filename] + self.extra_args[1:]
        try:
            if os.path.isfile(full_filename):
                self.log.info("Running file in user namespace: %s" %
                              full_filename)
                # Ensure that __file__ is always defined to match Python
                # behavior.
                with preserve_keys(self.shell.user_ns, '__file__'):
                    self.shell.user_ns['__file__'] = fname
                    if full_filename.endswith('.ipy') or full_filename.endswith('.ipynb'):
                        self.shell.safe_execfile_ipy(full_filename,
                                                     shell_futures=shell_futures)
                    else:
                        # default to python, even without extension
                        self.shell.safe_execfile(full_filename,
                                                 self.shell.user_ns,
                                                 shell_futures=shell_futures,
                                                 raise_exceptions=True)
        finally:
            sys.argv = save_argv

    def _run_startup_files(self):
        """Run files from profile startup directory"""
        startup_dirs = [self.profile_dir.startup_dir] + [
            os.path.join(p, 'startup') for p in chain(ENV_CONFIG_DIRS, SYSTEM_CONFIG_DIRS)
        ]
        startup_files = []

        if self.exec_PYTHONSTARTUP and os.environ.get('PYTHONSTARTUP', False) and \
                not (self.file_to_run or self.code_to_run or self.module_to_run):
```
