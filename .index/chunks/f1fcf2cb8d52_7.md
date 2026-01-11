# Chunk: f1fcf2cb8d52_7

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 562-655
- chunk: 8/13

```
 extension_manager = Unicode(
        "pypi",
        config=True,
        help="""The extension manager factory to use. The default options are:
        "readonly" for a manager without installation capability or "pypi" for
        a manager using PyPi.org and pip to install extensions.""",
    )

    watch = Bool(False, config=True, help="Whether to serve the app in watch mode")

    skip_dev_build = Bool(
        False,
        config=True,
        help="Whether to skip the initial install and JS build of the app in dev mode",
    )

    splice_source = Bool(False, config=True, help="Splice source packages into app directory.")

    expose_app_in_browser = Bool(
        False,
        config=True,
        help="Whether to expose the global app instance to browser via window.jupyterapp",
    )

    custom_css = Bool(
        False,
        config=True,
        help="""Whether custom CSS is loaded on the page.
    Defaults to False.
    """,
    )

    collaborative = Bool(
        False,
        config=True,
        help="""To enable real-time collaboration, you must install the extension `jupyter_collaboration`.
        You can install it using pip for example:

            python -m pip install jupyter_collaboration

        This flag is now deprecated and will be removed in JupyterLab v5.""",
    )

    news_url = Unicode(
        "https://jupyterlab.github.io/assets/feed.xml",
        allow_none=True,
        help="""URL that serves news Atom feed; by default the JupyterLab organization announcements will be fetched. Set to None to turn off fetching announcements.""",
        config=True,
    )

    lock_all_plugins = Bool(
        False,
        config=True,
        help="Whether all plugins are locked (cannot be enabled/disabled from the UI)",
    )

    check_for_updates_class = Type(
        default_value=CheckForUpdate,
        klass=CheckForUpdateABC,
        config=True,
        help="""A callable class that receives the current version at instantiation and calling it must return asynchronously a string indicating which version is available and how to install or None if no update is available. The string supports Markdown format.""",
    )

    @default("app_dir")
    def _default_app_dir(self):
        app_dir = get_app_dir()
        if self.core_mode:
            app_dir = HERE
        elif self.dev_mode:
            app_dir = DEV_DIR
        return app_dir

    @default("app_settings_dir")
    def _default_app_settings_dir(self):
        return pjoin(self.app_dir, "settings")

    @default("app_version")
    def _default_app_version(self):
        return app_version

    @default("cache_files")
    def _default_cache_files(self):
        return False

    @default("schemas_dir")
    def _default_schemas_dir(self):
        return pjoin(self.app_dir, "schemas")

    @default("templates_dir")
    def _default_templates_dir(self):
        return pjoin(self.app_dir, "static")

    @default("themes_dir")
```
