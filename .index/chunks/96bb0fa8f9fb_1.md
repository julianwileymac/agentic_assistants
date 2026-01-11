# Chunk: 96bb0fa8f9fb_1

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 83-149
- chunk: 2/6

```
er_root = server_root.replace(os.sep, "/")
        base_url = self.settings.get("base_url")

        # Remove the trailing slash for compatibility with html-webpack-plugin.
        full_static_url = self.static_url_prefix.rstrip("/")
        page_config.setdefault("fullStaticUrl", full_static_url)

        page_config.setdefault("terminalsAvailable", terminals)
        page_config.setdefault("ignorePlugins", [])
        page_config.setdefault("serverRoot", server_root)
        page_config["store_id"] = self.application.store_id  # type:ignore[attr-defined]

        server_root = os.path.normpath(os.path.expanduser(server_root))
        preferred_path = ""
        try:
            preferred_path = self.serverapp.contents_manager.preferred_dir
        except Exception:
            # FIXME: Remove fallback once CM.preferred_dir is ubiquitous.
            try:
                # Remove the server_root from app pref dir
                if self.serverapp.preferred_dir and self.serverapp.preferred_dir != server_root:
                    preferred_path = (
                        pathlib.Path(self.serverapp.preferred_dir)
                        .relative_to(server_root)
                        .as_posix()
                    )
            except Exception:  # noqa: S110
                pass
        # JupyterLab relies on an unset/default path being "/"
        page_config["preferredPath"] = preferred_path or "/"

        self.application.store_id += 1  # type:ignore[attr-defined]

        mathjax_config = self.settings.get("mathjax_config", "TeX-AMS_HTML-full,Safe")
        # TODO Remove CDN usage.
        mathjax_url = self.mathjax_url
        if not mathjax_url:
            mathjax_url = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js"

        page_config.setdefault("mathjaxConfig", mathjax_config)
        page_config.setdefault("fullMathjaxUrl", mathjax_url)

        # Put all our config in page_config
        for name in config.trait_names():
            page_config[_camelCase(name)] = getattr(app, name)

        # Add full versions of all the urls
        for name in config.trait_names():
            if not name.endswith("_url"):
                continue
            full_name = _camelCase("full_" + name)
            full_url = getattr(app, name)
            if base_url is not None and not is_url(full_url):
                # Relative URL will be prefixed with base_url
                full_url = ujoin(base_url, full_url)
            page_config[full_name] = full_url

        # Update the page config with the data from disk
        labextensions_path = app.extra_labextensions_path + app.labextensions_path
        recursive_update(
            page_config, get_page_config(labextensions_path, settings_dir, logger=self.log)
        )

        # modify page config with custom hook
        page_config_hook = self.settings.get("page_config_hook", None)
        if page_config_hook:
```
