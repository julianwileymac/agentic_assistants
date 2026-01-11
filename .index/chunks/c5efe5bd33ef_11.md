# Chunk: c5efe5bd33ef_11

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 777-849
- chunk: 12/17

```
.warning("wrote error: %r", reply["message"], exc_info=True)
        self.finish(json.dumps(reply))

    def get_login_url(self) -> str:
        """Get the login url."""
        # if get_login_url is invoked in an API handler,
        # that means @web.authenticated is trying to trigger a redirect.
        # instead of redirecting, raise 403 instead.
        if not self.current_user:
            raise web.HTTPError(403)
        return super().get_login_url()

    @property
    def content_security_policy(self) -> str:
        csp = "; ".join(  # noqa: FLY002
            [
                super().content_security_policy,
                "default-src 'none'",
            ]
        )
        return csp

    # set _track_activity = False on API handlers that shouldn't track activity
    _track_activity = True

    def update_api_activity(self) -> None:
        """Update last_activity of API requests"""
        # record activity of authenticated requests
        if (
            self._track_activity
            and getattr(self, "_jupyter_current_user", None)
            and self.get_argument("no_track_activity", None) is None
        ):
            self.settings["api_last_activity"] = utcnow()

    def finish(self, *args: Any, **kwargs: Any) -> Future[Any]:
        """Finish an API response."""
        self.update_api_activity()
        # Allow caller to indicate content-type...
        set_content_type = kwargs.pop("set_content_type", "application/json")
        self.set_header("Content-Type", set_content_type)
        return super().finish(*args, **kwargs)

    @allow_unauthenticated
    def options(self, *args: Any, **kwargs: Any) -> None:
        """Get the options."""
        if "Access-Control-Allow-Headers" in self.settings.get("headers", {}):
            self.set_header(
                "Access-Control-Allow-Headers",
                self.settings["headers"]["Access-Control-Allow-Headers"],
            )
        else:
            self.set_header(
                "Access-Control-Allow-Headers",
                "accept, content-type, authorization, x-xsrftoken",
            )
        self.set_header("Access-Control-Allow-Methods", "GET, PUT, POST, PATCH, DELETE, OPTIONS")

        # if authorization header is requested,
        # that means the request is token-authenticated.
        # avoid browser-side rejection of the preflight request.
        # only allow this exception if allow_origin has not been specified
        # and Jupyter server authentication is enabled.
        # If the token is not valid, the 'real' request will still be rejected.
        requested_headers = self.request.headers.get("Access-Control-Request-Headers", "").split(
            ","
        )
        if (
            requested_headers
            and any(h.strip().lower() == "authorization" for h in requested_headers)
            and (
                # FIXME: it would be even better to check specifically for token-auth,
```
