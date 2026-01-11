# Chunk: 8eb2c67fee2e_8

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 522-601
- chunk: 9/17

```
tern) is None:
            SetuptoolsDeprecationWarning.emit(
                "Please provide a valid glob pattern.",
                "Pattern {pattern!r} contains invalid characters.",
                pattern=pattern,
                see_url=f"https://packaging.python.org/en/latest/{pypa_guides}",
                due_date=(2026, 3, 20),  # Introduced in 2025-02-20
            )

        found = glob(pattern, recursive=True)

        if enforce_match and not found:
            SetuptoolsDeprecationWarning.emit(
                "Cannot find any files for the given pattern.",
                "Pattern {pattern!r} did not match any files.",
                pattern=pattern,
                due_date=(2026, 3, 20),  # Introduced in 2025-02-20
                # PEP 639 requires us to error, but as a transition period
                # we will only issue a warning to give people time to prepare.
                # After the transition, this should raise an InvalidConfigError.
            )
        return found

    # FIXME: 'Distribution._parse_config_files' is too complex (14)
    def _parse_config_files(self, filenames=None):  # noqa: C901
        """
        Adapted from distutils.dist.Distribution.parse_config_files,
        this method provides the same functionality in subtly-improved
        ways.
        """
        from configparser import ConfigParser

        # Ignore install directory options if we have a venv
        ignore_options = (
            []
            if sys.prefix == sys.base_prefix
            else [
                'install-base',
                'install-platbase',
                'install-lib',
                'install-platlib',
                'install-purelib',
                'install-headers',
                'install-scripts',
                'install-data',
                'prefix',
                'exec-prefix',
                'home',
                'user',
                'root',
            ]
        )

        ignore_options = frozenset(ignore_options)

        if filenames is None:
            filenames = self.find_config_files()

        if DEBUG:
            self.announce("Distribution.parse_config_files():")

        parser = ConfigParser()
        parser.optionxform = str
        for filename in filenames:
            with open(filename, encoding='utf-8') as reader:
                if DEBUG:
                    self.announce("  reading {filename}".format(**locals()))
                parser.read_file(reader)
            for section in parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)

                for opt in options:
                    if opt == '__name__' or opt in ignore_options:
                        continue

                    val = parser.get(section, opt)
                    opt = self._enforce_underscore(opt, section)
                    opt = self._enforce_option_lowercase(opt, section)
```
