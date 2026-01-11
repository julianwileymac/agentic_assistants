# Chunk: c5efe5bd33ef_9

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 639-708
- chunk: 10/17

```
thod:
                raise HTTPError(403)
            method = getattr(self, self.request.method.lower())
            if not getattr(method, "__allow_unauthenticated", False):
                if _redirect_to_login:
                    # reuse `web.authenticated` logic, which redirects to the login
                    # page on GET and HEAD and otherwise raises 403
                    return web.authenticated(lambda _: super().prepare())(self)
                else:
                    # raise 403 if user is not known without redirecting to login page
                    user = self.current_user
                    if user is None:
                        self.log.warning(
                            f"Couldn't authenticate {self.__class__.__name__} connection"
                        )
                        raise web.HTTPError(403)

        return super().prepare()

    # ---------------------------------------------------------------
    # template rendering
    # ---------------------------------------------------------------

    def get_template(self, name):
        """Return the jinja template object for a given name"""
        return self.settings["jinja2_env"].get_template(name)

    def render_template(self, name, **ns):
        """Render a template by name."""
        ns.update(self.template_namespace)
        template = self.get_template(name)
        return template.render(**ns)

    @property
    def template_namespace(self) -> dict[str, Any]:
        return dict(
            base_url=self.base_url,
            default_url=self.default_url,
            ws_url=self.ws_url,
            logged_in=self.logged_in,
            allow_password_change=getattr(self.identity_provider, "allow_password_change", False),
            auth_enabled=self.identity_provider.auth_enabled,
            login_available=self.identity_provider.login_available,
            token_available=bool(self.token),
            static_url=self.static_url,
            sys_info=json_sys_info(),
            contents_js_source=self.contents_js_source,
            version_hash=self.version_hash,
            xsrf_form_html=self.xsrf_form_html,
            token=self.token,
            xsrf_token=self.xsrf_token.decode("utf8"),
            nbjs_translations=json.dumps(
                combine_translations(self.request.headers.get("Accept-Language", ""))
            ),
            **self.jinja_template_vars,
        )

    def get_json_body(self) -> dict[str, Any] | None:
        """Return the body of the request as JSON data."""
        if not self.request.body:
            return None
        # Do we need to call body.decode('utf-8') here?
        body = self.request.body.strip().decode("utf-8")
        try:
            model = json.loads(body)
        except Exception as e:
            self.log.debug("Bad JSON: %r", body)
            self.log.error("Couldn't parse JSON", exc_info=True)
            raise web.HTTPError(400, "Invalid JSON in body of request") from e
```
