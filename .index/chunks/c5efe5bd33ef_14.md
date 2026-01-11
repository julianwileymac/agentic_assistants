# Chunk: c5efe5bd33ef_14

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 992-1076
- chunk: 15/17

```
ent]

    def set_headers(self) -> None:
        """Set the headers."""
        super().set_headers()

        immutable_paths = self.settings.get("static_immutable_cache", [])

        # allow immutable cache for files
        if any(self.request.path.startswith(path) for path in immutable_paths):
            self.set_header("Cache-Control", "public, max-age=31536000, immutable")

        # disable browser caching, rely on 304 replies for savings
        elif "v" not in self.request.arguments or any(
            self.request.path.startswith(path) for path in self.no_cache_paths
        ):
            self.set_header("Cache-Control", "no-cache")

    def initialize(
        self,
        path: str | list[str],
        default_filename: str | None = None,
        no_cache_paths: list[str] | None = None,
    ) -> None:
        """Initialize the file find handler."""
        self.no_cache_paths = no_cache_paths or []

        if isinstance(path, str):
            path = [path]

        self.root = tuple(os.path.abspath(os.path.expanduser(p)) + os.sep for p in path)  # type:ignore[assignment]
        self.default_filename = default_filename

    def compute_etag(self) -> str | None:
        """Compute the etag."""
        return None

    # access is allowed as this class is used to serve static assets on login page
    # TODO: create an allow-list of files used on login page and remove this decorator
    @allow_unauthenticated
    def get(self, path: str, include_body: bool = True) -> Coroutine[Any, Any, None]:
        return super().get(path, include_body)

    # access is allowed as this class is used to serve static assets on login page
    # TODO: create an allow-list of files used on login page and remove this decorator
    @allow_unauthenticated
    def head(self, path: str) -> Awaitable[None]:
        return super().head(path)

    @classmethod
    def get_absolute_path(cls, roots: Sequence[str], path: str) -> str:
        """locate a file to serve on our static file search path"""
        with cls._lock:
            if path in cls._static_paths:
                return cls._static_paths[path]
            try:
                abspath = os.path.abspath(filefind(path, roots))
            except OSError:
                # IOError means not found
                return ""

            cls._static_paths[path] = abspath

            log().debug(f"Path {path} served from {abspath}")
            return abspath

    def validate_absolute_path(self, root: str, absolute_path: str) -> str | None:
        """check if the file should be served (raises 404, 403, etc.)"""
        if not absolute_path:
            raise web.HTTPError(404)

        for root in self.root:
            if (absolute_path + os.sep).startswith(root):
                break

        return super().validate_absolute_path(root, absolute_path)


class APIVersionHandler(APIHandler):
    """An API handler for the server version."""

    _track_activity = False

    @allow_unauthenticated
```
