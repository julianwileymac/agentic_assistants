# Chunk: c429bff9dea7_1

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/listings_handler.py`
- lines: 67-93
- chunk: 2/2

```
educes the guards in the methods using
    them.
    """
    # The list of blocked_extensions URIS.
    blocked_extensions_uris: set = set()
    # The list of allowed_extensions URIS.
    allowed_extensions_uris: set = set()
    # The blocked extensions extensions.
    blocked_extensions: list = []
    # The allowed extensions extensions.
    allowed_extensions: list = []
    # The provider request options to be used for the request library.
    listings_request_opts: dict = {}
    # The callback time for the periodic callback in seconds.
    listings_refresh_seconds: int
    # The PeriodicCallback that schedule the call to fetch_listings method.
    pc = None

    @tornado.web.authenticated
    def get(self, path: str) -> None:
        """Get the listings for the extension manager."""
        self.set_header("Content-Type", "application/json")
        if path == LISTINGS_URL_SUFFIX:
            self.write(ListingsHandler.listings)  # type:ignore[attr-defined]
        else:
            raise tornado.web.HTTPError(400)
```
