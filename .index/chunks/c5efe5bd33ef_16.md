# Chunk: c5efe5bd33ef_16

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 1146-1212
- chunk: 17/17

```
enticated
    async def get(self, path: str = "") -> None:
        return await self.redirect_to_files(self, path)


class RedirectWithParams(web.RequestHandler):
    """Same as web.RedirectHandler, but preserves URL parameters"""

    def initialize(self, url: str, permanent: bool = True) -> None:
        """Initialize a redirect handler."""
        self._url = url
        self._permanent = permanent

    @allow_unauthenticated
    def get(self) -> None:
        """Get a redirect."""
        sep = "&" if "?" in self._url else "?"
        url = sep.join([self._url, self.request.query])
        self.redirect(url, permanent=self._permanent)


class PrometheusMetricsHandler(JupyterHandler):
    """
    Return prometheus metrics for this server
    """

    @allow_unauthenticated
    def get(self) -> None:
        """Get prometheus metrics."""
        if self.settings["authenticate_prometheus"] and not self.logged_in:
            raise web.HTTPError(403)

        self.set_header("Content-Type", prometheus_client.CONTENT_TYPE_LATEST)
        self.write(prometheus_client.generate_latest(prometheus_client.REGISTRY))


class PublicStaticFileHandler(web.StaticFileHandler):
    """Same as web.StaticFileHandler, but decorated to acknowledge that auth is not required."""

    @allow_unauthenticated
    def head(self, path: str) -> Awaitable[None]:
        return super().head(path)

    @allow_unauthenticated
    def get(self, path: str, include_body: bool = True) -> Coroutine[Any, Any, None]:
        return super().get(path, include_body)


# -----------------------------------------------------------------------------
# URL pattern fragments for reuse
# -----------------------------------------------------------------------------

# path matches any number of `/foo[/bar...]` or just `/` or ''
path_regex = r"(?P<path>(?:(?:/[^/]+)+|/?))"

# -----------------------------------------------------------------------------
# URL to handler mappings
# -----------------------------------------------------------------------------


default_handlers = [
    (r".*/", TrailingSlashHandler),
    (r"api", APIVersionHandler),
    (r"/(robots\.txt|favicon\.ico)", PublicStaticFileHandler),
    (r"/metrics", PrometheusMetricsHandler),
]
```
