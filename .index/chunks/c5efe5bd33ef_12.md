# Chunk: c5efe5bd33ef_12

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 841-927
- chunk: 13/17

```
ess-Control-Request-Headers", "").split(
            ","
        )
        if (
            requested_headers
            and any(h.strip().lower() == "authorization" for h in requested_headers)
            and (
                # FIXME: it would be even better to check specifically for token-auth,
                # but there is currently no API for this.
                self.login_available
            )
            and (
                self.allow_origin
                or self.allow_origin_pat
                or "Access-Control-Allow-Origin" in self.settings.get("headers", {})
            )
        ):
            self.set_header("Access-Control-Allow-Origin", self.request.headers.get("Origin", ""))


class Template404(JupyterHandler):
    """Render our 404 template"""

    async def prepare(self) -> None:  # type:ignore[override]
        """Prepare a 404 response."""
        await super().prepare()
        raise web.HTTPError(404)


class AuthenticatedFileHandler(JupyterHandler, web.StaticFileHandler):
    """static files should only be accessible when logged in"""

    auth_resource = "contents"

    @property
    def content_security_policy(self) -> str:
        # In case we're serving HTML/SVG, confine any Javascript to a unique
        # origin so it can't interact with the Jupyter server.
        return super().content_security_policy + "; sandbox allow-scripts"

    @web.authenticated
    @authorized
    def head(self, path: str) -> Awaitable[None]:  # type:ignore[override]
        """Get the head response for a path."""
        self.check_xsrf_cookie()
        return super().head(path)

    @web.authenticated
    @authorized
    def get(  # type:ignore[override]
        self, path: str, **kwargs: Any
    ) -> Awaitable[None]:
        """Get a file by path."""
        self.check_xsrf_cookie()
        if os.path.splitext(path)[1] == ".ipynb" or self.get_argument("download", None):
            name = path.rsplit("/", 1)[-1]
            self.set_attachment_header(name)

        return web.StaticFileHandler.get(self, path, **kwargs)

    def get_content_type(self) -> str:
        """Get the content type."""
        assert self.absolute_path is not None
        path = self.absolute_path.strip("/")
        if "/" in path:
            _, name = path.rsplit("/", 1)
        else:
            name = path
        if name.endswith(".ipynb"):
            return "application/x-ipynb+json"
        else:
            cur_mime = mimetypes.guess_type(name)[0]
            if cur_mime == "text/plain":
                return "text/plain; charset=UTF-8"
            else:
                return super().get_content_type()

    def set_headers(self) -> None:
        """Set the headers."""
        super().set_headers()
        # disable browser caching, rely on 304 replies for savings
        if "v" not in self.request.arguments:
            self.add_header("Cache-Control", "no-cache")

    def compute_etag(self) -> str | None:
        """Compute the etag."""
```
