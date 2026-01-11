# Chunk: ebda9f2aadce_2

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 178-262
- chunk: 3/8

```
           build(
                    clean_staging=self.should_clean,
                    production=production,
                    minimize=self.minimize,
                    app_options=app_options,
                )

    def run_task(self):
        pass

    def deprecation_warning(self, msg):
        return self.log.warning(
            f"\033[33m(Deprecated) {msg}\n\n{LABEXTENSION_COMMAND_WARNING} \033[0m"
        )

    def _log_format_default(self):
        """A default format for messages"""
        return "%(message)s"


class InstallLabExtensionApp(BaseExtensionApp):
    description = """Install labextension(s)

     Usage

        jupyter labextension install [--pin-version-as <alias,...>] <package...>

    This installs JupyterLab extensions similar to yarn add or npm install.

    Pass a list of comma separate names to the --pin-version-as flag
    to use as aliases for the packages providers. This is useful to
    install multiple versions of the same extension.
    These can be uninstalled with the alias you provided
    to the flag, similar to the "alias" feature of yarn add.
    """
    aliases = install_aliases

    pin = Unicode("", config=True, help="Pin this version with a certain alias")

    def run_task(self):
        self.deprecation_warning(
            "Installing extensions with the jupyter labextension install command is now deprecated and will be removed in a future major version of JupyterLab."
        )
        pinned_versions = self.pin.split(",")
        self.extra_args = self.extra_args or [os.getcwd()]
        return any(
            install_extension(
                arg,
                # Pass in pinned alias if we have it
                pin=pinned_versions[i] if i < len(pinned_versions) else None,
                app_options=AppOptions(
                    app_dir=self.app_dir,
                    logger=self.log,
                    core_config=self.core_config,
                    labextensions_path=self.labextensions_path,
                ),
            )
            for i, arg in enumerate(self.extra_args)
        )


class DevelopLabExtensionApp(BaseExtensionApp):
    description = "(developer) Develop labextension"
    flags = develop_flags

    user = Bool(False, config=True, help="Whether to do a user install")
    sys_prefix = Bool(True, config=True, help="Use the sys.prefix as the prefix")
    overwrite = Bool(False, config=True, help="Whether to overwrite files")
    symlink = Bool(True, config=False, help="Whether to use a symlink")

    labextensions_dir = Unicode(
        "",
        config=True,
        help="Full path to labextensions dir (probably use prefix or user)",
    )

    def run_task(self):
        """Add config for this labextension"""
        self.extra_args = self.extra_args or [os.getcwd()]
        for arg in self.extra_args:
            develop_labextension_py(
                arg,
                user=self.user,
                sys_prefix=self.sys_prefix,
```
