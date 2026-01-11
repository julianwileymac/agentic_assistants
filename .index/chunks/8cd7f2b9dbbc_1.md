# Chunk: 8cd7f2b9dbbc_1

- source: `.venv-lab/Lib/site-packages/jupyter_server/extension/handler.py`
- lines: 86-151
- chunk: 2/3

```
render_template(self, name: str, **ns) -> str:
        """Override render template to handle static_paths

        If render_template is called with a template from the base environment
        (e.g. default error pages)
        make sure our extension-specific static_url is _not_ used.
        """
        template = cast(Template, self.get_template(name))  # type:ignore[attr-defined]
        ns.update(self.template_namespace)  # type:ignore[attr-defined]
        if template.environment is self.settings["jinja2_env"]:
            # default template environment, use default static_url
            ns["static_url"] = super().static_url  # type:ignore[misc]
        return cast(str, template.render(**ns))

    @property
    def static_url_prefix(self) -> str:
        return self.extensionapp.static_url_prefix

    @property
    def static_path(self) -> str:
        return cast(str, self.settings[f"{self.name}_static_paths"])

    def static_url(self, path: str, include_host: bool | None = None, **kwargs: Any) -> str:
        """Returns a static URL for the given relative static file path.
        This method requires you set the ``{name}_static_path``
        setting in your extension (which specifies the root directory
        of your static files).
        This method returns a versioned url (by default appending
        ``?v=<signature>``), which allows the static files to be
        cached indefinitely.  This can be disabled by passing
        ``include_version=False`` (in the default implementation;
        other static file implementations are not required to support
        this, but they may support other options).
        By default this method returns URLs relative to the current
        host, but if ``include_host`` is true the URL returned will be
        absolute.  If this handler has an ``include_host`` attribute,
        that value will be used as the default for all `static_url`
        calls that do not pass ``include_host`` as a keyword argument.
        """
        key = f"{self.name}_static_paths"
        try:
            self.require_setting(key, "static_url")  # type:ignore[attr-defined]
        except Exception as e:
            if key in self.settings:
                msg = (
                    "This extension doesn't have any static paths listed. Check that the "
                    "extension's `static_paths` trait is set."
                )
                raise Exception(msg) from None
            else:
                raise e

        get_url = self.settings.get("static_handler_class", FileFindHandler).make_static_url

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        base = ""
        if include_host:
            base = self.request.protocol + "://" + self.request.host  # type:ignore[attr-defined]

        # Hijack settings dict to send extension templates to extension
        # static directory.
        settings = {
            "static_path": self.static_path,
```
