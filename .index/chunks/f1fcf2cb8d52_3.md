# Chunk: f1fcf2cb8d52_3

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 253-350
- chunk: 4/13

```
 = clean_aliases
    flags = clean_flags

    # Not configurable!
    core_config = Instance(CoreConfig, allow_none=True)

    app_dir = Unicode("", config=True, help="The app directory to clean")

    extensions = Bool(False, config=True, help=f"Also delete <app-dir>/extensions.\n{ext_warn_msg}")

    settings = Bool(False, config=True, help="Also delete <app-dir>/settings")

    static = Bool(False, config=True, help="Also delete <app-dir>/static")

    all = Bool(
        False,
        config=True,
        help=f"Delete the entire contents of the app directory.\n{ext_warn_msg}",
    )

    def start(self):
        app_options = LabCleanAppOptions(
            logger=self.log,
            core_config=self.core_config,
            app_dir=self.app_dir,
            extensions=self.extensions,
            settings=self.settings,
            static=self.static,
            all=self.all,
        )
        clean(app_options=app_options)


class LabPathApp(JupyterApp):
    version = version
    description = """
    Print the configured paths for the JupyterLab application

    The application path can be configured using the JUPYTERLAB_DIR
        environment variable.
    The user settings path can be configured using the JUPYTERLAB_SETTINGS_DIR
        environment variable or it will fall back to
        `/lab/user-settings` in the default Jupyter configuration directory.
    The workspaces path can be configured using the JUPYTERLAB_WORKSPACES_DIR
        environment variable or it will fall back to
        '/lab/workspaces' in the default Jupyter configuration directory.
    """

    def start(self):
        print(f"Application directory:   {get_app_dir()}")
        print(f"User Settings directory: {get_user_settings_dir()}")
        print(f"Workspaces directory: {get_workspaces_dir()}")


class LabWorkspaceExportApp(WorkspaceExportApp):
    version = version

    @default("workspaces_dir")
    def _default_workspaces_dir(self):
        return get_workspaces_dir()


class LabWorkspaceImportApp(WorkspaceImportApp):
    version = version

    @default("workspaces_dir")
    def _default_workspaces_dir(self):
        return get_workspaces_dir()


class LabWorkspaceListApp(WorkspaceListApp):
    version = version

    @default("workspaces_dir")
    def _default_workspaces_dir(self):
        return get_workspaces_dir()


class LabWorkspaceApp(JupyterApp):
    version = version
    description = """
    Import or export a JupyterLab workspace or list all the JupyterLab workspaces

    There are three sub-commands for export, import or listing of workspaces. This app
        should not otherwise do any work.
    """
    subcommands = {}
    subcommands["export"] = (
        LabWorkspaceExportApp,
        LabWorkspaceExportApp.description.splitlines()[0],
    )
    subcommands["import"] = (
        LabWorkspaceImportApp,
        LabWorkspaceImportApp.description.splitlines()[0],
    )
    subcommands["list"] = (
        LabWorkspaceListApp,
```
