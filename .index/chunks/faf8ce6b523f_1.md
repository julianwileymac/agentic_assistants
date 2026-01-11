# Chunk: faf8ce6b523f_1

- source: `.venv-lab/Lib/site-packages/IPython/core/profiledir.py`
- lines: 75-168
- chunk: 2/4

```
n path

        This is a version of os.mkdir, with the following differences:

        - returns whether the directory has been created or not.
        - ignores EEXIST, protecting against race conditions where
          the dir may have been created in between the check and
          the creation
        - sets permissions if requested and the dir already exists

        Parameters
        ----------
        path: str
            path of the dir to create
        mode: int
            see `mode` of `os.mkdir`

        Returns
        -------
        bool:
            returns True if it created the directory, False otherwise
        """

        if os.path.exists(path):
            if mode and os.stat(path).st_mode != mode:
                try:
                    os.chmod(path, mode)
                except OSError:
                    self.log.warning(
                        "Could not set permissions on %s",
                        path
                    )
            return False
        try:
            if mode:
                os.mkdir(path, mode)
            else:
                os.mkdir(path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                return False
            else:
                raise

        return True
    
    @observe('log_dir')
    def check_log_dir(self, change=None):
        self._mkdir(self.log_dir)
    
    @observe('startup_dir')
    def check_startup_dir(self, change=None):
        if self._mkdir(self.startup_dir):
            readme = os.path.join(self.startup_dir, "README")
            src = os.path.join(
                get_ipython_package_dir(), "core", "profile", "README_STARTUP"
            )

            if os.path.exists(src):
                if not os.path.exists(readme):
                    shutil.copy(src, readme)
            else:
                self.log.warning(
                    "Could not copy README_STARTUP to startup dir. Source file %s does not exist.",
                    src,
                )

    @observe('security_dir')
    def check_security_dir(self, change=None):
        self._mkdir(self.security_dir, 0o40700)

    @observe('pid_dir')
    def check_pid_dir(self, change=None):
        self._mkdir(self.pid_dir, 0o40700)

    def check_dirs(self):
        self.check_security_dir()
        self.check_log_dir()
        self.check_pid_dir()
        self.check_startup_dir()

    def copy_config_file(self, config_file: str, path: Path, overwrite=False) -> bool:
        """Copy a default config file into the active profile directory.

        Default configuration files are kept in :mod:`IPython.core.profile`.
        This function moves these from that location to the working profile
        directory.
        """
        dst = Path(os.path.join(self.location, config_file))
        if dst.exists() and not overwrite:
            return False
        if path is None:
            path = os.path.join(get_ipython_package_dir(), u'core', u'profile', u'default')
```
