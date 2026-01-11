# Chunk: c5efe5bd33ef_13

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 919-1002
- chunk: 14/17

```
  """Set the headers."""
        super().set_headers()
        # disable browser caching, rely on 304 replies for savings
        if "v" not in self.request.arguments:
            self.add_header("Cache-Control", "no-cache")

    def compute_etag(self) -> str | None:
        """Compute the etag."""
        return None

    def validate_absolute_path(self, root: str, absolute_path: str) -> str:
        """Validate and return the absolute path.

        Requires tornado 3.1

        Adding to tornado's own handling, forbids the serving of hidden files.
        """
        abs_path = super().validate_absolute_path(root, absolute_path)
        abs_root = os.path.abspath(root)
        assert abs_path is not None
        if not self.contents_manager.allow_hidden and is_hidden(abs_path, abs_root):
            self.log.info(
                "Refusing to serve hidden file, via 404 Error, use flag 'ContentsManager.allow_hidden' to enable"
            )
            raise web.HTTPError(404)
        return abs_path


def json_errors(method: Any) -> Any:  # pragma: no cover
    """Decorate methods with this to return GitHub style JSON errors.

    This should be used on any JSON API on any handler method that can raise HTTPErrors.

    This will grab the latest HTTPError exception using sys.exc_info
    and then:

    1. Set the HTTP status code based on the HTTPError
    2. Create and return a JSON body with a message field describing
       the error in a human readable form.
    """
    warnings.warn(
        "@json_errors is deprecated in notebook 5.2.0. Subclass APIHandler instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.write_error = types.MethodType(APIHandler.write_error, self)
        return method(self, *args, **kwargs)

    return wrapper


# -----------------------------------------------------------------------------
# File handler
# -----------------------------------------------------------------------------

# to minimize subclass changes:
HTTPError = web.HTTPError


class FileFindHandler(JupyterHandler, web.StaticFileHandler):
    """subclass of StaticFileHandler for serving files from a search path

    The setting "static_immutable_cache" can be set up to serve some static
    file as immutable (e.g. file name containing a hash). The setting is a
    list of base URL, every static file URL starting with one of those will
    be immutable.
    """

    # cache search results, don't search for files more than once
    _static_paths: dict[str, str] = {}
    root: tuple[str]  # type:ignore[assignment]

    def set_headers(self) -> None:
        """Set the headers."""
        super().set_headers()

        immutable_paths = self.settings.get("static_immutable_cache", [])

        # allow immutable cache for files
        if any(self.request.path.startswith(path) for path in immutable_paths):
```
