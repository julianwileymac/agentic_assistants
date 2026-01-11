# Chunk: c5efe5bd33ef_6

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 433-517
- chunk: 7/17

```
ado is present because tornado requires
    # check_origin to take an origin argument, but we don't use it
    def check_origin(self, origin_to_satisfy_tornado: str = "") -> bool:
        """Check Origin for cross-site API requests, including websockets

        Copied from WebSocket with changes:

        - allow unspecified host/origin (e.g. scripts)
        - allow token-authenticated requests
        """
        if self.allow_origin == "*" or self.skip_check_origin():
            return True

        host = self.request.headers.get("Host")
        origin = self.request.headers.get("Origin")

        # If no header is provided, let the request through.
        # Origin can be None for:
        # - same-origin (IE, Firefox)
        # - Cross-site POST form (IE, Firefox)
        # - Scripts
        # The cross-site POST (XSRF) case is handled by tornado's xsrf_token
        if origin is None or host is None:
            return True

        origin = origin.lower()
        origin_host = urlparse(origin).netloc

        # OK if origin matches host
        if origin_host == host:
            return True

        # Check CORS headers
        if self.allow_origin:
            allow = bool(self.allow_origin == origin)
        elif self.allow_origin_pat:
            allow = bool(re.match(self.allow_origin_pat, origin))
        else:
            # No CORS headers deny the request
            allow = False
        if not allow:
            self.log.warning(
                "Blocking Cross Origin API request for %s.  Origin: %s, Host: %s",
                self.request.path,
                origin,
                host,
            )
        return allow

    def check_referer(self) -> bool:
        """Check Referer for cross-site requests.
        Disables requests to certain endpoints with
        external or missing Referer.
        If set, allow_origin settings are applied to the Referer
        to whitelist specific cross-origin sites.
        Used on GET for api endpoints and /files/
        to block cross-site inclusion (XSSI).
        """
        if self.allow_origin == "*" or self.skip_check_origin():
            return True

        host = self.request.headers.get("Host")
        referer = self.request.headers.get("Referer")

        if not host:
            self.log.warning("Blocking request with no host")
            return False
        if not referer:
            self.log.warning("Blocking request with no referer")
            return False

        referer_url = urlparse(referer)
        referer_host = referer_url.netloc
        if referer_host == host:
            return True

        # apply cross-origin checks to Referer:
        origin = f"{referer_url.scheme}://{referer_url.netloc}"
        if self.allow_origin:
            allow = self.allow_origin == origin
        elif self.allow_origin_pat:
            allow = bool(re.match(self.allow_origin_pat, origin))
        else:
            # No CORS settings, deny the request
```
