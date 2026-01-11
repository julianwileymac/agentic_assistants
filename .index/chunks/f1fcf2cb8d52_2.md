# Chunk: f1fcf2cb8d52_2

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 169-263
- chunk: 3/13

```
ild in dev mode. Defaults to True (dev mode) if there are any locally linked extensions, else defaults to False (production mode).",
    )

    minimize = Bool(
        True,
        config=True,
        help="Whether to minimize a production build (defaults to True).",
    )

    pre_clean = Bool(
        False, config=True, help="Whether to clean before building (defaults to False)"
    )

    splice_source = Bool(False, config=True, help="Splice source packages into app directory.")

    def start(self):
        app_dir = self.app_dir or get_app_dir()
        app_options = AppOptions(
            app_dir=app_dir,
            logger=self.log,
            core_config=self.core_config,
            splice_source=self.splice_source,
        )
        self.log.info(f"JupyterLab {version}")
        with self.debug_logging():
            if self.pre_clean:
                self.log.info(f"Cleaning {app_dir}")
                clean(app_options=app_options)
            self.log.info(f"Building in {app_dir}")
            try:
                production = None if self.dev_build is None else not self.dev_build
                build(
                    name=self.name,
                    version=self.version,
                    app_options=app_options,
                    production=production,
                    minimize=self.minimize,
                )
            except Exception as e:
                self.log.error(build_failure_msg)
                raise e


clean_aliases = dict(base_aliases)
clean_aliases["app-dir"] = "LabCleanApp.app_dir"

ext_warn_msg = "WARNING: this will delete all of your extensions, which will need to be reinstalled"

clean_flags = dict(base_flags)
clean_flags["extensions"] = (
    {"LabCleanApp": {"extensions": True}},
    f"Also delete <app-dir>/extensions.\n{ext_warn_msg}",
)
clean_flags["settings"] = (
    {"LabCleanApp": {"settings": True}},
    "Also delete <app-dir>/settings",
)
clean_flags["static"] = (
    {"LabCleanApp": {"static": True}},
    "Also delete <app-dir>/static",
)
clean_flags["all"] = (
    {"LabCleanApp": {"all": True}},
    f"Delete the entire contents of the app directory.\n{ext_warn_msg}",
)


class LabCleanAppOptions(AppOptions):
    extensions = Bool(False)
    settings = Bool(False)
    staging = Bool(True)
    static = Bool(False)
    all = Bool(False)


class LabCleanApp(JupyterApp):
    version = version
    description = """
    Clean the JupyterLab application

    This will clean the app directory by removing the `staging` directories.
    Optionally, the `extensions`, `settings`, and/or `static` directories,
    or the entire contents of the app directory, can also be removed.
    """
    aliases = clean_aliases
    flags = clean_flags

    # Not configurable!
    core_config = Instance(CoreConfig, allow_none=True)

    app_dir = Unicode("", config=True, help="The app directory to clean")

    extensions = Bool(False, config=True, help=f"Also delete <app-dir>/extensions.\n{ext_warn_msg}")
```
