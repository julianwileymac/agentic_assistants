# Chunk: ebda9f2aadce_6

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 485-573
- chunk: 7/8

```
ck labextension(s) by name"
    aliases = lock_aliases

    level = Unicode("sys_prefix", help="Level at which to lock: sys_prefix, user, system").tag(
        config=True
    )

    def run_task(self):
        app_options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            core_config=self.core_config,
            labextensions_path=self.labextensions_path,
        )
        [lock_extension(arg, app_options=app_options, level=self.level) for arg in self.extra_args]


class UnlockLabExtensionsApp(BaseExtensionApp):
    description = "Unlock labextension(s) by name"
    aliases = unlock_aliases

    level = Unicode("sys_prefix", help="Level at which to unlock: sys_prefix, user, system").tag(
        config=True
    )

    def run_task(self):
        app_options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            core_config=self.core_config,
            labextensions_path=self.labextensions_path,
        )
        [
            unlock_extension(arg, app_options=app_options, level=self.level)
            for arg in self.extra_args
        ]


class CheckLabExtensionsApp(BaseExtensionApp):
    description = "Check labextension(s) by name"
    flags = check_flags

    should_check_installed_only = Bool(
        False,
        config=True,
        help="Whether it should check only if the extensions is installed",
    )

    def run_task(self):
        app_options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            core_config=self.core_config,
            labextensions_path=self.labextensions_path,
        )
        all_enabled = all(
            check_extension(
                arg, installed=self.should_check_installed_only, app_options=app_options
            )
            for arg in self.extra_args
        )
        if not all_enabled:
            self.exit(1)


_EXAMPLES = """
jupyter labextension list                        # list all configured labextensions
jupyter labextension install <extension name>    # install a labextension
jupyter labextension uninstall <extension name>  # uninstall a labextension
jupyter labextension develop                     # (developer) develop a prebuilt labextension
jupyter labextension build                       # (developer) build a prebuilt labextension
jupyter labextension watch                       # (developer) watch a prebuilt labextension
"""


class LabExtensionApp(JupyterApp):
    """Base jupyter labextension command entry point"""

    name = "jupyter labextension"
    version = VERSION
    description = "Work with JupyterLab extensions"
    examples = _EXAMPLES

    subcommands = {
        "install": (InstallLabExtensionApp, "Install labextension(s)"),
        "update": (UpdateLabExtensionApp, "Update labextension(s)"),
        "uninstall": (UninstallLabExtensionApp, "Uninstall labextension(s)"),
        "list": (ListLabExtensionsApp, "List labextensions"),
```
