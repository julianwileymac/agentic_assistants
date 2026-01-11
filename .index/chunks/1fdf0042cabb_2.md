# Chunk: 1fdf0042cabb_2

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/workspaces_app.py`
- lines: 164-193
- chunk: 3/3

```
  file_name = self.extra_args[0]

        if file_name == "-":  # pragma: no cover
            return sys.stdin

        file_path = Path(file_name).resolve()

        if not file_path.exists():  # pragma: no cover
            self.log.info("%s does not exist.", file_name)
            self.exit(1)

        return file_path.open(encoding="utf-8")

    def _validate(self, data: Any) -> Any:
        workspace = json.load(data)

        if "data" not in workspace:
            msg = "The `data` field is missing."
            raise Exception(msg)

        # If workspace_name is set in config, inject the
        # name into the workspace metadata.
        if self.workspace_name is not None and self.workspace_name:
            workspace["metadata"] = {"id": self.workspace_name}
        elif "id" not in workspace["metadata"]:
            msg = "The `id` field is missing in `metadata`."
            raise Exception(msg)

        return workspace
```
