# Chunk: c5efe5bd33ef_1

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 87-166
- chunk: 2/17

```
ef base_url(self) -> str:
        return cast(str, self.settings.get("base_url", "/"))

    @property
    def content_security_policy(self) -> str:
        """The default Content-Security-Policy header

        Can be overridden by defining Content-Security-Policy in settings['headers']
        """
        if "Content-Security-Policy" in self.settings.get("headers", {}):
            # user-specified, don't override
            return cast(str, self.settings["headers"]["Content-Security-Policy"])

        return "; ".join(
            [
                "frame-ancestors 'self'",
                # Make sure the report-uri is relative to the base_url
                "report-uri "
                + self.settings.get("csp_report_uri", url_path_join(self.base_url, csp_report_uri)),
            ]
        )

    def set_default_headers(self) -> None:
        """Set the default headers."""
        headers = {}
        headers["X-Content-Type-Options"] = "nosniff"
        headers.update(self.settings.get("headers", {}))

        headers["Content-Security-Policy"] = self.content_security_policy

        # Allow for overriding headers
        for header_name, value in headers.items():
            try:
                self.set_header(header_name, value)
            except Exception as e:
                # tornado raise Exception (not a subclass)
                # if method is unsupported (websocket and Access-Control-Allow-Origin
                # for example, so just ignore)
                self.log.exception(  # type:ignore[attr-defined]
                    "Could not set default headers: %s", e
                )

    @property
    def cookie_name(self) -> str:
        warnings.warn(
            """JupyterHandler.login_handler is deprecated in 2.0,
            use JupyterHandler.identity_provider.
            """,
            DeprecationWarning,
            stacklevel=2,
        )
        return self.identity_provider.get_cookie_name(self)

    def force_clear_cookie(self, name: str, path: str = "/", domain: str | None = None) -> None:
        """Force a cookie clear."""
        warnings.warn(
            """JupyterHandler.login_handler is deprecated in 2.0,
            use JupyterHandler.identity_provider.
            """,
            DeprecationWarning,
            stacklevel=2,
        )
        self.identity_provider._force_clear_cookie(self, name, path=path, domain=domain)

    def clear_login_cookie(self) -> None:
        """Clear a login cookie."""
        warnings.warn(
            """JupyterHandler.login_handler is deprecated in 2.0,
            use JupyterHandler.identity_provider.
            """,
            DeprecationWarning,
            stacklevel=2,
        )
        self.identity_provider.clear_login_cookie(self)

    def get_current_user(self) -> str:
        """Get the current user."""
        clsname = self.__class__.__name__
        msg = (
```
