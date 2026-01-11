# Chunk: 8cd7f2b9dbbc_0

- source: `.venv-lab/Lib/site-packages/jupyter_server/extension/handler.py`
- lines: 1-93
- chunk: 1/3

```
"""An extension handler."""

from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Any, cast

from jinja2 import Template
from jinja2.exceptions import TemplateNotFound

from jupyter_server.base.handlers import FileFindHandler

if TYPE_CHECKING:
    from traitlets.config import Config

    from jupyter_server.extension.application import ExtensionApp
    from jupyter_server.serverapp import ServerApp


class ExtensionHandlerJinjaMixin:
    """Mixin class for ExtensionApp handlers that use jinja templating for
    template rendering.
    """

    def get_template(self, name: str) -> Template:
        """Return the jinja template object for a given name"""
        try:
            env = f"{self.name}_jinja2_env"  # type:ignore[attr-defined]
            template = cast(Template, self.settings[env].get_template(name))  # type:ignore[attr-defined]
            return template
        except TemplateNotFound:
            return cast(Template, super().get_template(name))  # type:ignore[misc]


class ExtensionHandlerMixin:
    """Base class for Jupyter server extension handlers.

    Subclasses can serve static files behind a namespaced
    endpoint: "<base_url>/static/<name>/"

    This allows multiple extensions to serve static files under
    their own namespace and avoid intercepting requests for
    other extensions.
    """

    settings: dict[str, Any]

    def initialize(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.name = name
        try:
            super().initialize(*args, **kwargs)  # type:ignore[misc]
        except TypeError:
            pass

    @property
    def extensionapp(self) -> ExtensionApp:
        return cast("ExtensionApp", self.settings[self.name])

    @property
    def serverapp(self) -> ServerApp:
        key = "serverapp"
        return cast("ServerApp", self.settings[key])

    @property
    def log(self) -> Logger:
        if not hasattr(self, "name"):
            return cast(Logger, super().log)  # type:ignore[misc]
        # Attempt to pull the ExtensionApp's log, otherwise fall back to ServerApp.
        try:
            return cast(Logger, self.extensionapp.log)
        except AttributeError:
            return cast(Logger, self.serverapp.log)

    @property
    def config(self) -> Config:
        return cast("Config", self.settings[f"{self.name}_config"])

    @property
    def server_config(self) -> Config:
        return cast("Config", self.settings["config"])

    @property
    def base_url(self) -> str:
        return cast(str, self.settings.get("base_url", "/"))

    def render_template(self, name: str, **ns) -> str:
        """Override render template to handle static_paths

        If render_template is called with a template from the base environment
        (e.g. default error pages)
        make sure our extension-specific static_url is _not_ used.
        """
```
