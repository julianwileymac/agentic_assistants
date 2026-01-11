# Chunk: ebda9f2aadce_4

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 331-412
- chunk: 5/8

```
   core_path=self.core_path or None,
        )


class UpdateLabExtensionApp(BaseExtensionApp):
    description = "Update labextension(s)"
    flags = update_flags

    all = Bool(False, config=True, help="Whether to update all extensions")

    def run_task(self):
        self.deprecation_warning(
            "Updating extensions with the jupyter labextension update command is now deprecated and will be removed in a future major version of JupyterLab."
        )
        if not self.all and not self.extra_args:
            self.log.warning(
                "Specify an extension to update, or use --all to update all extensions"
            )
            return False
        app_options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            core_config=self.core_config,
            labextensions_path=self.labextensions_path,
        )
        if self.all:
            return update_extension(all_=True, app_options=app_options)
        return any(update_extension(name=arg, app_options=app_options) for arg in self.extra_args)


class LinkLabExtensionApp(BaseExtensionApp):
    description = """
    Link local npm packages that are not lab extensions.

    Links a package to the JupyterLab build process. A linked
    package is manually re-installed from its source location when
    `jupyter lab build` is run.
    """
    should_build = Bool(True, config=True, help="Whether to build the app after the action")

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            labextensions_path=self.labextensions_path,
            core_config=self.core_config,
        )
        return any(link_package(arg, app_options=options) for arg in self.extra_args)


class UnlinkLabExtensionApp(BaseExtensionApp):
    description = "Unlink packages by name or path"

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            labextensions_path=self.labextensions_path,
            core_config=self.core_config,
        )
        return any(unlink_package(arg, app_options=options) for arg in self.extra_args)


class UninstallLabExtensionApp(BaseExtensionApp):
    description = "Uninstall labextension(s) by name"
    flags = uninstall_flags

    all = Bool(False, config=True, help="Whether to uninstall all extensions")

    def run_task(self):
        self.deprecation_warning(
            "Uninstalling extensions with the jupyter labextension uninstall command is now deprecated and will be removed in a future major version of JupyterLab."
        )
        self.extra_args = self.extra_args or [os.getcwd()]

        options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            labextensions_path=self.labextensions_path,
```
