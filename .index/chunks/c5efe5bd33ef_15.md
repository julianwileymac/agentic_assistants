# Chunk: c5efe5bd33ef_15

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 1063-1155
- chunk: 16/17

```
.root:
            if (absolute_path + os.sep).startswith(root):
                break

        return super().validate_absolute_path(root, absolute_path)


class APIVersionHandler(APIHandler):
    """An API handler for the server version."""

    _track_activity = False

    @allow_unauthenticated
    def get(self) -> None:
        """Get the server version info."""
        # not authenticated, so give as few info as possible
        self.finish(json.dumps({"version": jupyter_server.__version__}))


class TrailingSlashHandler(web.RequestHandler):
    """Simple redirect handler that strips trailing slashes

    This should be the first, highest priority handler.
    """

    @allow_unauthenticated
    def get(self) -> None:
        """Handle trailing slashes in a get."""
        assert self.request.uri is not None
        path, *rest = self.request.uri.partition("?")
        # trim trailing *and* leading /
        # to avoid misinterpreting repeated '//'
        path = "/" + path.strip("/")
        new_uri = "".join([path, *rest])
        self.redirect(new_uri)

    post = put = get


class MainHandler(JupyterHandler):
    """Simple handler for base_url."""

    @allow_unauthenticated
    def get(self) -> None:
        """Get the main template."""
        html = self.render_template("main.html")
        self.write(html)

    post = put = get


class FilesRedirectHandler(JupyterHandler):
    """Handler for redirecting relative URLs to the /files/ handler"""

    @staticmethod
    async def redirect_to_files(self: Any, path: str) -> None:
        """make redirect logic a reusable static method

        so it can be called from other handlers.
        """
        cm = self.contents_manager
        if await ensure_async(cm.dir_exists(path)):
            # it's a *directory*, redirect to /tree
            url = url_path_join(self.base_url, "tree", url_escape(path))
        else:
            orig_path = path
            # otherwise, redirect to /files
            parts = path.split("/")

            if not await ensure_async(cm.file_exists(path=path)) and "files" in parts:
                # redirect without files/ iff it would 404
                # this preserves pre-2.0-style 'files/' links
                self.log.warning("Deprecated files/ URL: %s", orig_path)
                parts.remove("files")
                path = "/".join(parts)

            if not await ensure_async(cm.file_exists(path=path)):
                raise web.HTTPError(404)

            url = url_path_join(self.base_url, "files", url_escape(path))
        self.log.debug("Redirecting %s to %s", self.request.path, url)
        self.redirect(url)

    @allow_unauthenticated
    async def get(self, path: str = "") -> None:
        return await self.redirect_to_files(self, path)


class RedirectWithParams(web.RequestHandler):
    """Same as web.RedirectHandler, but preserves URL parameters"""

    def initialize(self, url: str, permanent: bool = True) -> None:
```
