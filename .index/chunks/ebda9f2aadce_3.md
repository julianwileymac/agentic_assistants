# Chunk: ebda9f2aadce_3

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 254-343
- chunk: 4/8

```
    def run_task(self):
        """Add config for this labextension"""
        self.extra_args = self.extra_args or [os.getcwd()]
        for arg in self.extra_args:
            develop_labextension_py(
                arg,
                user=self.user,
                sys_prefix=self.sys_prefix,
                labextensions_dir=self.labextensions_dir,
                logger=self.log,
                overwrite=self.overwrite,
                symlink=self.symlink,
            )


class BuildLabExtensionApp(BaseExtensionApp):
    description = "(developer) Build labextension"

    static_url = Unicode("", config=True, help="Sets the url for static assets when building")

    development = Bool(False, config=True, help="Build in development mode")

    source_map = Bool(False, config=True, help="Generate source maps")

    core_path = Unicode(
        os.path.join(HERE, "staging"),
        config=True,
        help="Directory containing core application package.json file",
    )

    aliases = {
        "static-url": "BuildLabExtensionApp.static_url",
        "development": "BuildLabExtensionApp.development",
        "source-map": "BuildLabExtensionApp.source_map",
        "core-path": "BuildLabExtensionApp.core_path",
    }

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        build_labextension(
            self.extra_args[0],
            logger=self.log,
            development=self.development,
            static_url=self.static_url or None,
            source_map=self.source_map,
            core_path=self.core_path or None,
        )


class WatchLabExtensionApp(BaseExtensionApp):
    description = "(developer) Watch labextension"

    development = Bool(True, config=True, help="Build in development mode")

    source_map = Bool(False, config=True, help="Generate source maps")

    core_path = Unicode(
        os.path.join(HERE, "staging"),
        config=True,
        help="Directory containing core application package.json file",
    )

    aliases = {
        "core-path": "WatchLabExtensionApp.core_path",
        "development": "WatchLabExtensionApp.development",
        "source-map": "WatchLabExtensionApp.source_map",
    }

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        labextensions_path = self.labextensions_path
        watch_labextension(
            self.extra_args[0],
            labextensions_path,
            logger=self.log,
            development=self.development,
            source_map=self.source_map,
            core_path=self.core_path or None,
        )


class UpdateLabExtensionApp(BaseExtensionApp):
    description = "Update labextension(s)"
    flags = update_flags

    all = Bool(False, config=True, help="Whether to update all extensions")

    def run_task(self):
        self.deprecation_warning(
```
