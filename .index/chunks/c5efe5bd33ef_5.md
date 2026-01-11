# Chunk: c5efe5bd33ef_5

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 367-440
- chunk: 6/17

```
 CORS
    # ---------------------------------------------------------------

    @property
    def allow_origin(self) -> str:
        """Normal Access-Control-Allow-Origin"""
        return cast(str, self.settings.get("allow_origin", ""))

    @property
    def allow_origin_pat(self) -> str | None:
        """Regular expression version of allow_origin"""
        return cast("str | None", self.settings.get("allow_origin_pat", None))

    @property
    def allow_credentials(self) -> bool:
        """Whether to set Access-Control-Allow-Credentials"""
        return cast(bool, self.settings.get("allow_credentials", False))

    def set_default_headers(self) -> None:
        """Add CORS headers, if defined"""
        super().set_default_headers()

    def set_cors_headers(self) -> None:
        """Add CORS headers, if defined

        Now that current_user is async (jupyter-server 2.0),
        must be called at the end of prepare(), instead of in set_default_headers.
        """
        if self.allow_origin:
            self.set_header("Access-Control-Allow-Origin", self.allow_origin)
        elif self.allow_origin_pat:
            origin = self.get_origin()
            if origin and re.match(self.allow_origin_pat, origin):
                self.set_header("Access-Control-Allow-Origin", origin)
        elif self.token_authenticated and "Access-Control-Allow-Origin" not in self.settings.get(
            "headers", {}
        ):
            # allow token-authenticated requests cross-origin by default.
            # only apply this exception if allow-origin has not been specified.
            self.set_header("Access-Control-Allow-Origin", self.request.headers.get("Origin", ""))

        if self.allow_credentials:
            self.set_header("Access-Control-Allow-Credentials", "true")

    def set_attachment_header(self, filename: str) -> None:
        """Set Content-Disposition: attachment header

        As a method to ensure handling of filename encoding
        """
        escaped_filename = url_escape(filename)
        self.set_header(
            "Content-Disposition",
            f"attachment; filename*=utf-8''{escaped_filename}",
        )

    def get_origin(self) -> str | None:
        # Handle WebSocket Origin naming convention differences
        # The difference between version 8 and 13 is that in 8 the
        # client sends a "Sec-Websocket-Origin" header and in 13 it's
        # simply "Origin".
        if "Origin" in self.request.headers:
            origin = self.request.headers.get("Origin")
        else:
            origin = self.request.headers.get("Sec-Websocket-Origin", None)
        return origin

    # origin_to_satisfy_tornado is present because tornado requires
    # check_origin to take an origin argument, but we don't use it
    def check_origin(self, origin_to_satisfy_tornado: str = "") -> bool:
        """Check Origin for cross-site API requests, including websockets

        Copied from WebSocket with changes:
```
