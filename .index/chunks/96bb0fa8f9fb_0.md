# Chunk: 96bb0fa8f9fb_0

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 1-90
- chunk: 1/6

```
"""JupyterLab Server handlers"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import os
import pathlib
import warnings
from functools import lru_cache
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from jupyter_server.base.handlers import FileFindHandler, JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin
from jupyter_server.utils import url_path_join as ujoin
from tornado import template, web

from .config import LabConfig, get_page_config, recursive_update
from .licenses_handler import LicensesHandler, LicensesManager
from .listings_handler import ListingsHandler, fetch_listings
from .settings_handler import SettingsHandler
from .settings_utils import _get_overrides
from .themes_handler import ThemesHandler
from .translations_handler import TranslationsHandler
from .workspaces_handler import WorkspacesHandler, WorkspacesManager

if TYPE_CHECKING:
    from .app import LabServerApp
# -----------------------------------------------------------------------------
# Module globals
# -----------------------------------------------------------------------------

MASTER_URL_PATTERN = (
    r"/(?P<mode>{}|doc)(?P<workspace>/workspaces/[a-zA-Z0-9\-\_]+)?(?P<tree>/tree/.*)?"
)

DEFAULT_TEMPLATE = template.Template(
    """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Error</title>
</head>
<body>
<h2>Cannot find template: "{{name}}"</h2>
<p>In "{{path}}"</p>
</body>
</html>
"""
)


def is_url(url: str) -> bool:
    """Test whether a string is a full url (e.g. https://nasa.gov)

    https://stackoverflow.com/a/52455972
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class LabHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    """Render the JupyterLab View."""

    @lru_cache  # noqa: B019
    def get_page_config(self) -> dict[str, Any]:
        """Construct the page config object"""
        self.application.store_id = getattr(  # type:ignore[attr-defined]
            self.application, "store_id", 0
        )
        config = LabConfig()
        app: LabServerApp = self.extensionapp  # type:ignore[assignment]
        settings_dir = app.app_settings_dir
        # Handle page config data.
        page_config = self.settings.setdefault("page_config_data", {})
        terminals = self.settings.get("terminals_available", False)
        server_root = self.settings.get("server_root_dir", "")
        server_root = server_root.replace(os.sep, "/")
        base_url = self.settings.get("base_url")

        # Remove the trailing slash for compatibility with html-webpack-plugin.
        full_static_url = self.static_url_prefix.rstrip("/")
        page_config.setdefault("fullStaticUrl", full_static_url)
```
