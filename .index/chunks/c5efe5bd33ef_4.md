# Chunk: c5efe5bd33ef_4

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 291-377
- chunk: 5/17

```
s."""
        return cast("dict[str, Any]", self.settings.get("jinja_template_vars", {}))

    @property
    def serverapp(self) -> ServerApp | None:
        return cast("ServerApp | None", self.settings["serverapp"])

    # ---------------------------------------------------------------
    # URLs
    # ---------------------------------------------------------------

    @property
    def version_hash(self) -> str:
        """The version hash to use for cache hints for static files"""
        return cast(str, self.settings.get("version_hash", ""))

    @property
    def mathjax_url(self) -> str:
        url = cast(str, self.settings.get("mathjax_url", ""))
        if not url or url_is_absolute(url):
            return url
        return url_path_join(self.base_url, url)

    @property
    def mathjax_config(self) -> str:
        return cast(str, self.settings.get("mathjax_config", "TeX-AMS-MML_HTMLorMML-full,Safe"))

    @property
    def default_url(self) -> str:
        return cast(str, self.settings.get("default_url", ""))

    @property
    def ws_url(self) -> str:
        return cast(str, self.settings.get("websocket_url", ""))

    @property
    def contents_js_source(self) -> str:
        self.log.debug(
            "Using contents: %s",
            self.settings.get("contents_js_source", "services/contents"),
        )
        return cast(str, self.settings.get("contents_js_source", "services/contents"))

    # ---------------------------------------------------------------
    # Manager objects
    # ---------------------------------------------------------------

    @property
    def kernel_manager(self) -> AsyncMappingKernelManager:
        return cast("AsyncMappingKernelManager", self.settings["kernel_manager"])

    @property
    def contents_manager(self) -> ContentsManager:
        return cast("ContentsManager", self.settings["contents_manager"])

    @property
    def session_manager(self) -> SessionManager:
        return cast("SessionManager", self.settings["session_manager"])

    @property
    def terminal_manager(self) -> TerminalManager:
        return cast("TerminalManager", self.settings["terminal_manager"])

    @property
    def kernel_spec_manager(self) -> KernelSpecManager:
        return cast("KernelSpecManager", self.settings["kernel_spec_manager"])

    @property
    def config_manager(self) -> ConfigManager:
        return cast("ConfigManager", self.settings["config_manager"])

    @property
    def event_logger(self) -> EventLogger:
        return cast("EventLogger", self.settings["event_logger"])

    # ---------------------------------------------------------------
    # CORS
    # ---------------------------------------------------------------

    @property
    def allow_origin(self) -> str:
        """Normal Access-Control-Allow-Origin"""
        return cast(str, self.settings.get("allow_origin", ""))

    @property
    def allow_origin_pat(self) -> str | None:
```
