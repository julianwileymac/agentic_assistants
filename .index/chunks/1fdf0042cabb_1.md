# Chunk: 1fdf0042cabb_1

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/workspaces_app.py`
- lines: 91-175
- chunk: 2/3

```
  If a workspace name is passed in, this command will export that workspace.
    If no workspace is found, this command will export an empty workspace.
    """

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the app."""
        super().initialize(*args, **kwargs)
        self.manager = WorkspacesManager(self.workspaces_dir)

    def start(self) -> None:
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for workspace export.")
            self.exit(1)

        raw = DEFAULT_WORKSPACE if not self.extra_args else self.extra_args[0]
        try:
            workspace = self.manager.load(raw)
            print(json.dumps(workspace))
        except Exception:  # pragma: no cover
            self.log.error(json.dumps(dict(data=dict(), metadata=dict(id=raw))))


class WorkspaceImportApp(JupyterApp, LabConfig):
    """A workspace import app."""

    version = __version__
    description = """
    Import a JupyterLab workspace

    This command will import a workspace from a JSON file. The format of the
        file must be the same as what the export functionality emits.
    """
    workspace_name = Unicode(
        None,
        config=True,
        allow_none=True,
        help="""
        Workspace name. If given, the workspace ID in the imported
        file will be replaced with a new ID pointing to this
        workspace name.
        """,
    )

    aliases = {"name": "WorkspaceImportApp.workspace_name"}

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the app."""
        super().initialize(*args, **kwargs)
        self.manager = WorkspacesManager(self.workspaces_dir)

    def start(self) -> None:
        """Start the app."""
        if len(self.extra_args) != 1:  # pragma: no cover
            self.log.info("One argument is required for workspace import.")
            self.exit(1)

        with self._smart_open() as fid:
            try:  # to load, parse, and validate the workspace file.
                workspace = self._validate(fid)
            except Exception as e:  # pragma: no cover
                self.log.info("%s is not a valid workspace:\n%s", fid.name, e)
                self.exit(1)

        try:
            workspace_path = self.manager.save(workspace["metadata"]["id"], json.dumps(workspace))
        except Exception as e:  # pragma: no cover
            self.log.info("Workspace could not be exported:\n%s", e)
            self.exit(1)

        self.log.info("Saved workspace: %s", workspace_path)

    def _smart_open(self) -> Any:
        file_name = self.extra_args[0]

        if file_name == "-":  # pragma: no cover
            return sys.stdin

        file_path = Path(file_name).resolve()

        if not file_path.exists():  # pragma: no cover
            self.log.info("%s does not exist.", file_name)
            self.exit(1)
```
