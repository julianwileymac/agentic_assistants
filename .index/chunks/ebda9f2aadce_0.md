# Chunk: ebda9f2aadce_0

- source: `.venv-lab/Lib/site-packages/jupyterlab/labextensions.py`
- lines: 1-111
- chunk: 1/8

```
"""Jupyter LabExtension Entry Points."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import sys
from copy import copy

from jupyter_core.application import JupyterApp, base_aliases, base_flags
from traitlets import Bool, Instance, List, Unicode, default

from jupyterlab.coreconfig import CoreConfig
from jupyterlab.debuglog import DebugLogFileMixin

from .commands import (
    HERE,
    AppOptions,
    build,
    check_extension,
    disable_extension,
    enable_extension,
    get_app_version,
    install_extension,
    link_package,
    list_extensions,
    lock_extension,
    uninstall_extension,
    unlink_package,
    unlock_extension,
    update_extension,
)
from .federated_labextensions import build_labextension, develop_labextension_py, watch_labextension
from .labapp import LabApp

flags = dict(base_flags)
flags["no-build"] = (
    {"BaseExtensionApp": {"should_build": False}},
    "Defer building the app after the action.",
)
flags["dev-build"] = (
    {"BaseExtensionApp": {"dev_build": True}},
    "Build in development mode.",
)
flags["no-minimize"] = (
    {"BaseExtensionApp": {"minimize": False}},
    "Do not minimize a production build.",
)
flags["clean"] = (
    {"BaseExtensionApp": {"should_clean": True}},
    "Cleanup intermediate files after the action.",
)
flags["splice-source"] = (
    {"BaseExtensionApp": {"splice_source": True}},
    "Splice source packages into app directory.",
)

check_flags = copy(flags)
check_flags["installed"] = (
    {"CheckLabExtensionsApp": {"should_check_installed_only": True}},
    "Check only if the extension is installed.",
)

develop_flags = copy(flags)
develop_flags["overwrite"] = (
    {"DevelopLabExtensionApp": {"overwrite": True}},
    "Overwrite files",
)

update_flags = copy(flags)
update_flags["all"] = (
    {"UpdateLabExtensionApp": {"all": True}},
    "Update all extensions",
)

uninstall_flags = copy(flags)
uninstall_flags["all"] = (
    {"UninstallLabExtensionApp": {"all": True}},
    "Uninstall all extensions",
)

list_flags = copy(flags)
list_flags["verbose"] = (
    {"ListLabExtensionsApp": {"verbose": True}},
    "Increase verbosity level",
)

aliases = dict(base_aliases)
aliases["app-dir"] = "BaseExtensionApp.app_dir"
aliases["dev-build"] = "BaseExtensionApp.dev_build"
aliases["minimize"] = "BaseExtensionApp.minimize"
aliases["debug-log-path"] = "DebugLogFileMixin.debug_log_path"

install_aliases = copy(aliases)
install_aliases["pin-version-as"] = "InstallLabExtensionApp.pin"

enable_aliases = copy(aliases)
enable_aliases["level"] = "EnableLabExtensionsApp.level"

disable_aliases = copy(aliases)
disable_aliases["level"] = "DisableLabExtensionsApp.level"

lock_aliases = copy(aliases)
lock_aliases["level"] = "LockLabExtensionsApp.level"

unlock_aliases = copy(aliases)
unlock_aliases["level"] = "UnlockLabExtensionsApp.level"

VERSION = get_app_version()
```
