# Chunk: f1fcf2cb8d52_8

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 643-724
- chunk: 9/13

```
efault_cache_files(self):
        return False

    @default("schemas_dir")
    def _default_schemas_dir(self):
        return pjoin(self.app_dir, "schemas")

    @default("templates_dir")
    def _default_templates_dir(self):
        return pjoin(self.app_dir, "static")

    @default("themes_dir")
    def _default_themes_dir(self):
        if self.override_theme_url:
            return ""
        return pjoin(self.app_dir, "themes")

    @default("static_dir")
    def _default_static_dir(self):
        return pjoin(self.app_dir, "static")

    @default("static_url_prefix")
    def _default_static_url_prefix(self):
        if self.override_static_url:
            return self.override_static_url
        else:
            static_url = f"/static/{self.name}/"
            return ujoin(self.serverapp.base_url, static_url)

    @default("theme_url")
    def _default_theme_url(self):
        if self.override_theme_url:
            return self.override_theme_url
        return ""

    def initialize_templates(self):
        # Determine which model to run JupyterLab
        if self.core_mode or self.app_dir.startswith(HERE + os.sep):
            self.core_mode = True
            self.log.info("Running JupyterLab in core mode")

        if self.dev_mode or self.app_dir.startswith(DEV_DIR + os.sep):
            self.dev_mode = True
            self.log.info("Running JupyterLab in dev mode")

        if self.watch and self.core_mode:
            self.log.warning("Cannot watch in core mode, did you mean --dev-mode?")
            self.watch = False

        if self.core_mode and self.dev_mode:
            self.log.warning("Conflicting modes, choosing dev_mode over core_mode")
            self.core_mode = False

        # Set the paths based on JupyterLab's mode.
        if self.dev_mode:
            dev_static_dir = ujoin(DEV_DIR, "static")
            self.static_paths = [dev_static_dir]
            self.template_paths = [dev_static_dir]
            if not self.extensions_in_dev_mode:
                # Add an exception for @jupyterlab/galata-extension
                galata_extension = pjoin(HERE, "galata")
                self.labextensions_path = (
                    [galata_extension]
                    if galata_extension in map(os.path.abspath, self.labextensions_path)
                    else []
                )
                self.extra_labextensions_path = (
                    [galata_extension]
                    if galata_extension in map(os.path.abspath, self.extra_labextensions_path)
                    else []
                )
        elif self.core_mode:
            dev_static_dir = ujoin(HERE, "static")
            self.static_paths = [dev_static_dir]
            self.template_paths = [dev_static_dir]
            self.labextensions_path = []
            self.extra_labextensions_path = []
        else:
            self.static_paths = [self.static_dir]
            self.template_paths = [self.templates_dir]
```
