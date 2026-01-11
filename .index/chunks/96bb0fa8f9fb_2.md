# Chunk: 96bb0fa8f9fb_2

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 141-222
- chunk: 3/6

```
+ app.labextensions_path
        recursive_update(
            page_config, get_page_config(labextensions_path, settings_dir, logger=self.log)
        )

        # modify page config with custom hook
        page_config_hook = self.settings.get("page_config_hook", None)
        if page_config_hook:
            page_config = page_config_hook(self, page_config)

        return page_config

    @web.authenticated
    @web.removeslash
    def get(
        self, mode: str | None = None, workspace: str | None = None, tree: str | None = None
    ) -> None:
        """Get the JupyterLab html page."""
        workspace = "default" if workspace is None else workspace.replace("/workspaces/", "")
        tree_path = "" if tree is None else tree.replace("/tree/", "")

        page_config = self.get_page_config()

        # Add parameters parsed from the URL
        if mode == "doc":
            page_config["mode"] = "single-document"
        else:
            page_config["mode"] = "multiple-document"
        page_config["workspace"] = workspace
        page_config["treePath"] = tree_path

        # Write the template with the config.
        tpl = self.render_template("index.html", page_config=page_config)
        self.write(tpl)


class NotFoundHandler(LabHandler):
    """A handler for page not found."""

    @lru_cache  # noqa: B019
    def get_page_config(self) -> dict[str, Any]:
        """Get the page config."""
        # Making a copy of the page_config to ensure changes do not affect the original
        page_config = super().get_page_config().copy()
        page_config["notFoundUrl"] = self.request.path
        return page_config


def add_handlers(handlers: list[Any], extension_app: LabServerApp) -> None:
    """Add the appropriate handlers to the web app."""
    # Normalize directories.
    for name in LabConfig.class_trait_names():
        if not name.endswith("_dir"):
            continue
        value = getattr(extension_app, name)
        setattr(extension_app, name, value.replace(os.sep, "/"))

    # Normalize urls
    # Local urls should have a leading slash but no trailing slash
    for name in LabConfig.class_trait_names():
        if not name.endswith("_url"):
            continue
        value = getattr(extension_app, name)
        if is_url(value):
            continue
        if not value.startswith("/"):
            value = "/" + value
        if value.endswith("/"):
            value = value[:-1]
        setattr(extension_app, name, value)

    url_pattern = MASTER_URL_PATTERN.format(extension_app.app_url.replace("/", ""))
    handlers.append((url_pattern, LabHandler))

    # Cache all or none of the files depending on the `cache_files` setting.
    no_cache_paths = [] if extension_app.cache_files else ["/"]

    # Handle federated lab extensions.
    labextensions_path = extension_app.extra_labextensions_path + extension_app.labextensions_path
    labextensions_url = ujoin(extension_app.labextensions_url, "(.*)")
    handlers.append(
```
