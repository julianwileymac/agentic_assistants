# Chunk: f1fcf2cb8d52_0

- source: `.venv-lab/Lib/site-packages/jupyterlab/labapp.py`
- lines: 1-106
- chunk: 1/13

```
"""A tornado based Jupyter lab server."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import dataclasses
import json
import os
import sys

from jupyter_core.application import JupyterApp, NoStart, base_aliases, base_flags
from jupyter_server._version import version_info as jpserver_version_info
from jupyter_server.serverapp import flags
from jupyter_server.utils import url_path_join as ujoin
from jupyterlab_server import (
    LabServerApp,
    LicensesApp,
    WorkspaceExportApp,
    WorkspaceImportApp,
    WorkspaceListApp,
)
from jupyterlab_server.config import get_static_page_config
from notebook_shim.shim import NotebookConfigShimMixin
from traitlets import Bool, Instance, Type, Unicode, default

from ._version import __version__
from .commands import (
    DEV_DIR,
    HERE,
    AppOptions,
    build,
    clean,
    ensure_app,
    ensure_core,
    ensure_dev,
    get_app_dir,
    get_app_version,
    get_user_settings_dir,
    get_workspaces_dir,
    pjoin,
    watch,
    watch_dev,
)
from .coreconfig import CoreConfig
from .debuglog import DebugLogFileMixin
from .extensions import MANAGERS as EXT_MANAGERS
from .extensions.manager import PluginManager
from .extensions.readonly import ReadOnlyExtensionManager
from .handlers.announcements import (
    CheckForUpdate,
    CheckForUpdateABC,
    CheckForUpdateHandler,
    NewsHandler,
    check_update_handler_path,
    news_handler_path,
)
from .handlers.build_handler import Builder, BuildHandler, build_path
from .handlers.error_handler import ErrorHandler
from .handlers.extension_manager_handler import ExtensionHandler, extensions_handler_path
from .handlers.plugin_manager_handler import PluginHandler, plugins_handler_path

DEV_NOTE = """You're running JupyterLab from source.
If you're working on the TypeScript sources of JupyterLab, try running

    jupyter lab --dev-mode --watch


to have the system incrementally watch and build JupyterLab for you, as you
make changes.
"""


CORE_NOTE = """
Running the core application with no additional extensions or settings
"""

build_aliases = dict(base_aliases)
build_aliases["app-dir"] = "LabBuildApp.app_dir"
build_aliases["name"] = "LabBuildApp.name"
build_aliases["version"] = "LabBuildApp.version"
build_aliases["dev-build"] = "LabBuildApp.dev_build"
build_aliases["minimize"] = "LabBuildApp.minimize"
build_aliases["debug-log-path"] = "DebugLogFileMixin.debug_log_path"

build_flags = dict(base_flags)

build_flags["dev-build"] = (
    {"LabBuildApp": {"dev_build": True}},
    "Build in development mode.",
)
build_flags["no-minimize"] = (
    {"LabBuildApp": {"minimize": False}},
    "Do not minimize a production build.",
)
build_flags["splice-source"] = (
    {"LabBuildApp": {"splice_source": True}},
    "Splice source packages into app directory.",
)


version = __version__
app_version = get_app_version()
if version != app_version:
    version = f"{__version__} (dev), {app_version} (app)"
```
