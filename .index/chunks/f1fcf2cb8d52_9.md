# Chunk: f1fcf2cb8d52_9

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 716-786
- chunk: 10/13

```
    self.static_paths = [dev_static_dir]
            self.template_paths = [dev_static_dir]
            self.labextensions_path = []
            self.extra_labextensions_path = []
        else:
            self.static_paths = [self.static_dir]
            self.template_paths = [self.templates_dir]

    def _prepare_templates(self):
        super()._prepare_templates()
        self.jinja2_env.globals.update(custom_css=self.custom_css)

    def initialize_handlers(self):  # noqa
        handlers = []

        # Set config for Jupyterlab
        page_config = self.serverapp.web_app.settings.setdefault("page_config_data", {})
        page_config.update(get_static_page_config(logger=self.log, level="all"))

        page_config.setdefault("buildAvailable", not self.core_mode and not self.dev_mode)
        page_config.setdefault("buildCheck", not self.core_mode and not self.dev_mode)
        page_config["devMode"] = self.dev_mode
        page_config["token"] = self.serverapp.identity_provider.token
        page_config["exposeAppInBrowser"] = self.expose_app_in_browser
        page_config["quitButton"] = self.serverapp.quit_button
        page_config["allow_hidden_files"] = self.serverapp.contents_manager.allow_hidden
        if hasattr(self.serverapp.contents_manager, "delete_to_trash"):
            page_config["delete_to_trash"] = self.serverapp.contents_manager.delete_to_trash

        # Client-side code assumes notebookVersion is a JSON-encoded string
        page_config["notebookVersion"] = json.dumps(jpserver_version_info)

        self.log.info(f"JupyterLab extension loaded from {HERE!s}")
        self.log.info(f"JupyterLab application directory is {self.app_dir!s}")

        if self.custom_css:
            handlers.append(
                (
                    r"/custom/(.*)(?<!\.js)$",
                    self.serverapp.web_app.settings["static_handler_class"],
                    {
                        "path": self.serverapp.web_app.settings["static_custom_path"],
                        "no_cache_paths": ["/"],  # don't cache anything in custom
                    },
                )
            )

        app_options = AppOptions(
            logger=self.log,
            app_dir=self.app_dir,
            labextensions_path=self.extra_labextensions_path + self.labextensions_path,
            splice_source=self.splice_source,
        )
        builder = Builder(self.core_mode, app_options=app_options)
        build_handler = (build_path, BuildHandler, {"builder": builder})
        handlers.append(build_handler)

        errored = False

        if self.core_mode:
            self.log.info(CORE_NOTE.strip())
            ensure_core(self.log)
        elif self.dev_mode:
            if not (self.watch or self.skip_dev_build):
                ensure_dev(self.log)
                self.log.info(DEV_NOTE)
        else:
            if self.splice_source:
                ensure_dev(self.log)
            msgs = ensure_app(self.app_dir)
```
