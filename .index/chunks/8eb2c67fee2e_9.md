# Chunk: 8eb2c67fee2e_9

- source: `.venv-lab/Lib/site-packages/setuptools/dist.py`
- lines: 594-667
- chunk: 10/17

```
in options:
                    if opt == '__name__' or opt in ignore_options:
                        continue

                    val = parser.get(section, opt)
                    opt = self._enforce_underscore(opt, section)
                    opt = self._enforce_option_lowercase(opt, section)
                    opt_dict[opt] = (filename, val)

            # Make the ConfigParser forget everything (so we retain
            # the original filenames that options come from)
            parser.__init__()

        if 'global' not in self.command_options:
            return

        # If there was a "global" section in the config file, use it
        # to set Distribution options.

        for opt, (src, val) in self.command_options['global'].items():
            alias = self.negative_opt.get(opt)
            if alias:
                val = not strtobool(val)
            elif opt in ('verbose', 'dry_run'):  # ugh!
                val = strtobool(val)

            try:
                setattr(self, alias or opt, val)
            except ValueError as e:
                raise DistutilsOptionError(e) from e

    def _enforce_underscore(self, opt: str, section: str) -> str:
        if "-" not in opt or self._skip_setupcfg_normalization(section):
            return opt

        underscore_opt = opt.replace('-', '_')
        affected = f"(Affected: {self.metadata.name})." if self.metadata.name else ""
        SetuptoolsDeprecationWarning.emit(
            f"Invalid dash-separated key {opt!r} in {section!r} (setup.cfg), "
            f"please use the underscore name {underscore_opt!r} instead.",
            f"""
            Usage of dash-separated {opt!r} will not be supported in future
            versions. Please use the underscore name {underscore_opt!r} instead.
            {affected}
            """,
            see_docs="userguide/declarative_config.html",
            due_date=(2026, 3, 3),
            # Warning initially introduced in 3 Mar 2021
        )
        return underscore_opt

    def _enforce_option_lowercase(self, opt: str, section: str) -> str:
        if opt.islower() or self._skip_setupcfg_normalization(section):
            return opt

        lowercase_opt = opt.lower()
        affected = f"(Affected: {self.metadata.name})." if self.metadata.name else ""
        SetuptoolsDeprecationWarning.emit(
            f"Invalid uppercase key {opt!r} in {section!r} (setup.cfg), "
            f"please use lowercase {lowercase_opt!r} instead.",
            f"""
            Usage of uppercase key {opt!r} in {section!r} will not be supported in
            future versions. Please use lowercase {lowercase_opt!r} instead.
            {affected}
            """,
            see_docs="userguide/declarative_config.html",
            due_date=(2026, 3, 3),
            # Warning initially introduced in 6 Mar 2021
        )
        return lowercase_opt

    def _skip_setupcfg_normalization(self, section: str) -> bool:
        skip = (
```
