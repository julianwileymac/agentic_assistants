# Chunk: f1fcf2cb8d52_4

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 340-439
- chunk: 5/13

```
mmands["export"] = (
        LabWorkspaceExportApp,
        LabWorkspaceExportApp.description.splitlines()[0],
    )
    subcommands["import"] = (
        LabWorkspaceImportApp,
        LabWorkspaceImportApp.description.splitlines()[0],
    )
    subcommands["list"] = (
        LabWorkspaceListApp,
        LabWorkspaceListApp.description.splitlines()[0],
    )

    def start(self):
        try:
            super().start()
            self.log.error("One of `export`, `import` or `list` must be specified.")
            self.exit(1)
        except NoStart:
            pass
        self.exit(0)


class LabLicensesApp(LicensesApp):
    version = version

    dev_mode = Bool(
        False,
        config=True,
        help="""Whether to start the app in dev mode. Uses the unpublished local
        JavaScript packages in the `dev_mode` folder.  In this case JupyterLab will
        show a red stripe at the top of the page.  It can only be used if JupyterLab
        is installed as `pip install -e .`.
        """,
    )

    app_dir = Unicode("", config=True, help="The app directory for which to show licenses")

    aliases = {
        **LicensesApp.aliases,
        "app-dir": "LabLicensesApp.app_dir",
    }

    flags = {
        **LicensesApp.flags,
        "dev-mode": (
            {"LabLicensesApp": {"dev_mode": True}},
            "Start the app in dev mode for running from source.",
        ),
    }

    @default("app_dir")
    def _default_app_dir(self):
        return get_app_dir()

    @default("static_dir")
    def _default_static_dir(self):
        return pjoin(self.app_dir, "static")


aliases = dict(base_aliases)
aliases.update(
    {
        "ip": "ServerApp.ip",
        "port": "ServerApp.port",
        "port-retries": "ServerApp.port_retries",
        "keyfile": "ServerApp.keyfile",
        "certfile": "ServerApp.certfile",
        "client-ca": "ServerApp.client_ca",
        "notebook-dir": "ServerApp.root_dir",
        "browser": "ServerApp.browser",
        "pylab": "ServerApp.pylab",
    }
)


class LabApp(NotebookConfigShimMixin, LabServerApp):
    version = version

    name = "lab"
    app_name = "JupyterLab"

    # Should your extension expose other server extensions when launched directly?
    load_other_extensions = True

    description = """
    JupyterLab - An extensible computational environment for Jupyter.

    This launches a Tornado based HTML Server that serves up an
    HTML5/Javascript JupyterLab client.

    JupyterLab has three different modes of running:

    * Core mode (`--core-mode`): in this mode JupyterLab will run using the JavaScript
      assets contained in the installed `jupyterlab` Python package. In core mode, no
      extensions are enabled. This is the default in a stable JupyterLab release if you
      have no extensions installed.
    * Dev mode (`--dev-mode`): uses the unpublished local JavaScript packages in the
      `dev_mode` folder.  In this case JupyterLab will show a red stripe at the top of
```
