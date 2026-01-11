# Chunk: c5efe5bd33ef_3

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 231-300
- chunk: 4/17

```
t in self.settings:
            warnings.warn(
                "The Tornado web application does not have an 'authorizer' defined "
                "in its settings. In future releases of jupyter_server, this will "
                "be a required key for all subclasses of `JupyterHandler`. For an "
                "example, see the jupyter_server source code for how to "
                "add an authorizer to the tornado settings: "
                "https://github.com/jupyter-server/jupyter_server/blob/"
                "653740cbad7ce0c8a8752ce83e4d3c2c754b13cb/jupyter_server/serverapp.py"
                "#L234-L256",
                stacklevel=2,
            )
            from jupyter_server.auth import AllowAllAuthorizer

            self.settings["authorizer"] = AllowAllAuthorizer(
                config=self.settings.get("config", None),
                identity_provider=self.identity_provider,
            )

        return cast("Authorizer", self.settings.get("authorizer"))

    @property
    def identity_provider(self) -> IdentityProvider:
        if "identity_provider" not in self.settings:
            warnings.warn(
                "The Tornado web application does not have an 'identity_provider' defined "
                "in its settings. In future releases of jupyter_server, this will "
                "be a required key for all subclasses of `JupyterHandler`. For an "
                "example, see the jupyter_server source code for how to "
                "add an identity provider to the tornado settings: "
                "https://github.com/jupyter-server/jupyter_server/blob/v2.0.0/"
                "jupyter_server/serverapp.py#L242",
                stacklevel=2,
            )
            from jupyter_server.auth import IdentityProvider

            # no identity provider set, load default
            self.settings["identity_provider"] = IdentityProvider(
                config=self.settings.get("config", None)
            )
        return cast("IdentityProvider", self.settings["identity_provider"])


class JupyterHandler(AuthenticatedHandler):
    """Jupyter-specific extensions to authenticated handling

    Mostly property shortcuts to Jupyter-specific settings.
    """

    @property
    def config(self) -> dict[str, Any] | None:
        return cast("dict[str, Any] | None", self.settings.get("config", None))

    @property
    def log(self) -> Logger:
        """use the Jupyter log by default, falling back on tornado's logger"""
        return log()

    @property
    def jinja_template_vars(self) -> dict[str, Any]:
        """User-supplied values to supply to jinja templates."""
        return cast("dict[str, Any]", self.settings.get("jinja_template_vars", {}))

    @property
    def serverapp(self) -> ServerApp | None:
        return cast("ServerApp | None", self.settings["serverapp"])

    # ---------------------------------------------------------------
    # URLs
```
