# Chunk: 96bb0fa8f9fb_4

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 272-350
- chunk: 5/6

```
sHandler, workspaces_config))

        # Handle requests for an individually named workspace.
        workspace_api_path = ujoin(extension_app.workspaces_api_url, "(?P<space_name>.+)")
        handlers.append((workspace_api_path, WorkspacesHandler, workspaces_config))

    # Handle local listings.

    settings_config = extension_app.settings.get("config", {}).get("LabServerApp", {})
    blocked_extensions_uris: str = settings_config.get("blocked_extensions_uris", "")
    allowed_extensions_uris: str = settings_config.get("allowed_extensions_uris", "")

    if (blocked_extensions_uris) and (allowed_extensions_uris):
        warnings.warn(
            "Simultaneous blocked_extensions_uris and allowed_extensions_uris is not supported. Please define only one of those.",
            stacklevel=2,
        )
        import sys

        sys.exit(-1)

    ListingsHandler.listings_refresh_seconds = settings_config.get(
        "listings_refresh_seconds", 60 * 60
    )
    ListingsHandler.listings_request_opts = settings_config.get("listings_request_options", {})
    listings_url = ujoin(extension_app.listings_url)
    listings_path = ujoin(listings_url, "(.*)")

    if blocked_extensions_uris:
        ListingsHandler.blocked_extensions_uris = set(blocked_extensions_uris.split(","))
    if allowed_extensions_uris:
        ListingsHandler.allowed_extensions_uris = set(allowed_extensions_uris.split(","))

    fetch_listings(None)

    if (
        len(ListingsHandler.blocked_extensions_uris) > 0
        or len(ListingsHandler.allowed_extensions_uris) > 0
    ):
        from tornado import ioloop

        callback_time = ListingsHandler.listings_refresh_seconds * 1000
        ListingsHandler.pc = ioloop.PeriodicCallback(
            lambda: fetch_listings(None),  # type:ignore[assignment]
            callback_time=callback_time,
            jitter=0.1,
        )
        ListingsHandler.pc.start()  # type:ignore[attr-defined]

    handlers.append((listings_path, ListingsHandler, {}))

    # Handle local themes.
    if extension_app.themes_dir:
        themes_url = extension_app.themes_url
        themes_path = ujoin(themes_url, "(.*)")
        handlers.append(
            (
                themes_path,
                ThemesHandler,
                {
                    "themes_url": themes_url,
                    "path": extension_app.themes_dir,
                    "labextensions_path": labextensions_path,
                    "no_cache_paths": no_cache_paths,
                },
            )
        )

    # Handle licenses.
    if extension_app.licenses_url:
        licenses_url = extension_app.licenses_url
        licenses_path = ujoin(licenses_url, "(.*)")
        handlers.append(
            (licenses_path, LicensesHandler, {"manager": LicensesManager(parent=extension_app)})
        )

    # Let the lab handler act as the fallthrough option instead of a 404.
    fallthrough_url = ujoin(extension_app.app_url, r".*")
```
