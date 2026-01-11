# Chunk: c5efe5bd33ef_7

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 510-587
- chunk: 8/17

```
 origin = f"{referer_url.scheme}://{referer_url.netloc}"
        if self.allow_origin:
            allow = self.allow_origin == origin
        elif self.allow_origin_pat:
            allow = bool(re.match(self.allow_origin_pat, origin))
        else:
            # No CORS settings, deny the request
            allow = False

        if not allow:
            self.log.warning(
                "Blocking Cross Origin request for %s.  Referer: %s, Host: %s",
                self.request.path,
                origin,
                host,
            )
        return allow

    def check_xsrf_cookie(self) -> None:
        """Bypass xsrf cookie checks when token-authenticated"""
        if not hasattr(self, "_jupyter_current_user"):
            # Called too early, will be checked later
            return None
        if self.token_authenticated or self.settings.get("disable_check_xsrf", False):
            # Token-authenticated requests do not need additional XSRF-check
            # Servers without authentication are vulnerable to XSRF
            return None
        try:
            if not self.check_origin():
                raise web.HTTPError(404)
            return super().check_xsrf_cookie()
        except web.HTTPError as e:
            if self.request.method in {"GET", "HEAD"}:
                # Consider Referer a sufficient cross-origin check for GET requests
                if not self.check_referer():
                    referer = self.request.headers.get("Referer")
                    if referer:
                        msg = f"Blocking Cross Origin request from {referer}."
                    else:
                        msg = "Blocking request from unknown origin"
                    raise web.HTTPError(403, msg) from e
            else:
                raise

    def check_host(self) -> bool:
        """Check the host header if remote access disallowed.

        Returns True if the request should continue, False otherwise.
        """
        if self.settings.get("allow_remote_access", False):
            return True

        # Remove port (e.g. ':8888') from host
        match = re.match(r"^(.*?)(:\d+)?$", self.request.host)
        assert match is not None
        host = match.group(1)

        # Browsers format IPv6 addresses like [::1]; we need to remove the []
        if host.startswith("[") and host.endswith("]"):
            host = host[1:-1]

        # UNIX socket handling
        check_host = urldecode_unix_socket_path(host)
        if check_host.startswith("/") and os.path.exists(check_host):
            allow = True
        else:
            try:
                addr = ipaddress.ip_address(host)
            except ValueError:
                # Not an IP address: check against hostnames
                allow = host in self.settings.get("local_hostnames", ["localhost"])
            else:
                allow = addr.is_loopback

        if not allow:
            self.log.warning(
                (
```
