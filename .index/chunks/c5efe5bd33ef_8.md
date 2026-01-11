# Chunk: c5efe5bd33ef_8

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 578-645
- chunk: 9/17

```
      except ValueError:
                # Not an IP address: check against hostnames
                allow = host in self.settings.get("local_hostnames", ["localhost"])
            else:
                allow = addr.is_loopback

        if not allow:
            self.log.warning(
                (
                    "Blocking request with non-local 'Host' %s (%s). "
                    "If the server should be accessible at that name, "
                    "set ServerApp.allow_remote_access to disable the check."
                ),
                host,
                self.request.host,
            )
        return allow

    async def prepare(self, *, _redirect_to_login=True) -> Awaitable[None] | None:  # type:ignore[override]
        """Prepare a response."""
        # Set the current Jupyter Handler context variable.
        CallContext.set(CallContext.JUPYTER_HANDLER, self)

        if not self.check_host():
            self.current_user = self._jupyter_current_user = None
            raise web.HTTPError(403)

        from jupyter_server.auth import IdentityProvider

        mod_obj = inspect.getmodule(self.get_current_user)
        assert mod_obj is not None
        user: User | None = None

        if type(self.identity_provider) is IdentityProvider and mod_obj.__name__ != __name__:
            # check for overridden get_current_user + default IdentityProvider
            # deprecated way to override auth (e.g. JupyterHub < 3.0)
            # allow deprecated, overridden get_current_user
            warnings.warn(
                "Overriding JupyterHandler.get_current_user is deprecated in jupyter-server 2.0."
                " Use an IdentityProvider class.",
                DeprecationWarning,
                stacklevel=1,
            )
            user = User(self.get_current_user())
        else:
            _user = self.identity_provider.get_user(self)
            if isinstance(_user, Awaitable):
                # IdentityProvider.get_user _may_ be async
                _user = await _user
            user = _user

        # self.current_user for tornado's @web.authenticated
        # self._jupyter_current_user for backward-compat in deprecated get_current_user calls
        # and our own private checks for whether .current_user has been set
        self.current_user = self._jupyter_current_user = user
        # complete initial steps which require auth to resolve first:
        self.set_cors_headers()
        if self.request.method not in {"GET", "HEAD", "OPTIONS"}:
            self.check_xsrf_cookie()

        if not self.settings.get("allow_unauthenticated_access", False):
            if not self.request.method:
                raise HTTPError(403)
            method = getattr(self, self.request.method.lower())
            if not getattr(method, "__allow_unauthenticated", False):
                if _redirect_to_login:
                    # reuse `web.authenticated` logic, which redirects to the login
```
