# Chunk: ebda9f2aadce_5

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 404-496
- chunk: 6/8

```
 is now deprecated and will be removed in a future major version of JupyterLab."
        )
        self.extra_args = self.extra_args or [os.getcwd()]

        options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
            labextensions_path=self.labextensions_path,
            core_config=self.core_config,
        )
        return any(
            uninstall_extension(arg, all_=self.all, app_options=options) for arg in self.extra_args
        )


class ListLabExtensionsApp(BaseExtensionApp):
    description = "List the installed labextensions"
    verbose = Bool(False, help="Increase verbosity level.").tag(config=True)
    flags = list_flags

    def run_task(self):
        list_extensions(
            app_options=AppOptions(
                app_dir=self.app_dir,
                logger=self.log,
                core_config=self.core_config,
                labextensions_path=self.labextensions_path,
                verbose=self.verbose,
            )
        )


class EnableLabExtensionsApp(BaseExtensionApp):
    description = "Enable labextension(s) by name"
    aliases = enable_aliases

    level = Unicode("sys_prefix", help="Level at which to enable: sys_prefix, user, system").tag(
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
            enable_extension(arg, app_options=app_options, level=self.level)
            for arg in self.extra_args
        ]


class DisableLabExtensionsApp(BaseExtensionApp):
    description = "Disable labextension(s) by name"
    aliases = disable_aliases

    level = Unicode("sys_prefix", help="Level at which to disable: sys_prefix, user, system").tag(
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
            disable_extension(arg, app_options=app_options, level=self.level)
            for arg in self.extra_args
        ]
        self.log.info(
            "Starting with JupyterLab 4.1 individual plugins can be re-enabled"
            " in the user interface. While all plugins which were previously"
            " disabled have been locked, you need to explicitly lock any newly"
            " disabled plugins by using `jupyter labextension lock` command."
        )


class LockLabExtensionsApp(BaseExtensionApp):
    description = "Lock labextension(s) by name"
    aliases = lock_aliases

    level = Unicode("sys_prefix", help="Level at which to lock: sys_prefix, user, system").tag(
        config=True
    )

    def run_task(self):
        app_options = AppOptions(
            app_dir=self.app_dir,
            logger=self.log,
```
