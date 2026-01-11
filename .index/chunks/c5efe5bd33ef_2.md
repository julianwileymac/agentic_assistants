# Chunk: c5efe5bd33ef_2

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 155-236
- chunk: 3/17

```
ndler.identity_provider.
            """,
            DeprecationWarning,
            stacklevel=2,
        )
        self.identity_provider.clear_login_cookie(self)

    def get_current_user(self) -> str:
        """Get the current user."""
        clsname = self.__class__.__name__
        msg = (
            f"Calling `{clsname}.get_current_user()` directly is deprecated in jupyter-server 2.0."
            " Use `self.current_user` instead (works in all versions)."
        )
        if hasattr(self, "_jupyter_current_user"):
            # backward-compat: return _jupyter_current_user
            warnings.warn(
                msg,
                DeprecationWarning,
                stacklevel=2,
            )
            return cast(str, self._jupyter_current_user)
        # haven't called get_user in prepare, raise
        raise RuntimeError(msg)

    def skip_check_origin(self) -> bool:
        """Ask my login_handler if I should skip the origin_check

        For example: in the default LoginHandler, if a request is token-authenticated,
        origin checking should be skipped.
        """
        if self.request.method == "OPTIONS":
            # no origin-check on options requests, which are used to check origins!
            return True
        return not self.identity_provider.should_check_origin(self)

    @property
    def token_authenticated(self) -> bool:
        """Have I been authenticated with a token?"""
        return self.identity_provider.is_token_authenticated(self)

    @property
    def logged_in(self) -> bool:
        """Is a user currently logged in?"""
        user = self.current_user
        return bool(user and user != "anonymous")

    @property
    def login_handler(self) -> Any:
        """Return the login handler for this application, if any."""
        warnings.warn(
            """JupyterHandler.login_handler is deprecated in 2.0,
            use JupyterHandler.identity_provider.
            """,
            DeprecationWarning,
            stacklevel=2,
        )
        return self.identity_provider.login_handler_class

    @property
    def token(self) -> str | None:
        """Return the login token for this application, if any."""
        return self.identity_provider.token

    @property
    def login_available(self) -> bool:
        """May a user proceed to log in?

        This returns True if login capability is available, irrespective of
        whether the user is already logged in or not.

        """
        return cast(bool, self.identity_provider.login_available)

    @property
    def authorizer(self) -> Authorizer:
        if "authorizer" not in self.settings:
            warnings.warn(
                "The Tornado web application does not have an 'authorizer' defined "
                "in its settings. In future releases of jupyter_server, this will "
                "be a required key for all subclasses of `JupyterHandler`. For an "
```
