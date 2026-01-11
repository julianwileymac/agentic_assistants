# Chunk: 96bb0fa8f9fb_3

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 215-280
- chunk: 4/6

```
ing.
    no_cache_paths = [] if extension_app.cache_files else ["/"]

    # Handle federated lab extensions.
    labextensions_path = extension_app.extra_labextensions_path + extension_app.labextensions_path
    labextensions_url = ujoin(extension_app.labextensions_url, "(.*)")
    handlers.append(
        (
            labextensions_url,
            FileFindHandler,
            {"path": labextensions_path, "no_cache_paths": no_cache_paths},
        )
    )

    # Handle local settings.
    if extension_app.schemas_dir:
        # Load overrides once, rather than in each copy of the settings handler
        overrides, error = _get_overrides(extension_app.app_settings_dir)

        if error:
            overrides_warning = "Failed loading overrides: %s"
            extension_app.log.warning(overrides_warning, error)

        settings_config: dict[str, Any] = {
            "app_settings_dir": extension_app.app_settings_dir,
            "schemas_dir": extension_app.schemas_dir,
            "settings_dir": extension_app.user_settings_dir,
            "labextensions_path": labextensions_path,
            "overrides": overrides,
        }

        # Handle requests for the list of settings. Make slash optional.
        settings_path = ujoin(extension_app.settings_url, "?")
        handlers.append((settings_path, SettingsHandler, settings_config))

        # Handle requests for an individual set of settings.
        setting_path = ujoin(extension_app.settings_url, "(?P<schema_name>.+)")
        handlers.append((setting_path, SettingsHandler, settings_config))

        # Handle translations.
        # Translations requires settings as the locale source of truth is stored in it
        if extension_app.translations_api_url:
            # Handle requests for the list of language packs available.
            # Make slash optional.
            translations_path = ujoin(extension_app.translations_api_url, "?")
            handlers.append((translations_path, TranslationsHandler, settings_config))

            # Handle requests for an individual language pack.
            translations_lang_path = ujoin(extension_app.translations_api_url, "(?P<locale>.*)")
            handlers.append((translations_lang_path, TranslationsHandler, settings_config))

    # Handle saved workspaces.
    if extension_app.workspaces_dir:
        workspaces_config = {"manager": WorkspacesManager(extension_app.workspaces_dir)}

        # Handle requests for the list of workspaces. Make slash optional.
        workspaces_api_path = ujoin(extension_app.workspaces_api_url, "?")
        handlers.append((workspaces_api_path, WorkspacesHandler, workspaces_config))

        # Handle requests for an individually named workspace.
        workspace_api_path = ujoin(extension_app.workspaces_api_url, "(?P<space_name>.+)")
        handlers.append((workspace_api_path, WorkspacesHandler, workspaces_config))

    # Handle local listings.
```
