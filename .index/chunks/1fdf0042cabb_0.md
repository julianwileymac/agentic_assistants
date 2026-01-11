# Chunk: 1fdf0042cabb_0

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/workspaces_app.py`
- lines: 1-98
- chunk: 1/3

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""A workspace management CLI"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

from jupyter_core.application import JupyterApp
from traitlets import Bool, Unicode

from ._version import __version__
from .config import LabConfig
from .workspaces_handler import WorkspacesManager

# Default workspace ID
#  Needs to match PageConfig.defaultWorkspace define in packages/coreutils/src/pageconfig.ts
DEFAULT_WORKSPACE = "default"


class WorkspaceListApp(JupyterApp, LabConfig):
    """An app to list workspaces."""

    version = __version__
    description = """
    Print all the workspaces available

    If '--json' flag is passed in, a single 'json' object is printed.
    If '--jsonlines' flag is passed in, 'json' object of each workspace separated by a new line is printed.
    If nothing is passed in, workspace ids list is printed.
    """
    flags = dict(
        jsonlines=(
            {"WorkspaceListApp": {"jsonlines": True}},
            ("Produce machine-readable JSON Lines output."),
        ),
        json=(
            {"WorkspaceListApp": {"json": True}},
            ("Produce machine-readable JSON object output."),
        ),
    )

    jsonlines = Bool(
        False,
        config=True,
        help=(
            "If True, the output will be a newline-delimited JSON (see https://jsonlines.org/) of objects, "
            "one per JupyterLab workspace, each with the details of the relevant workspace"
        ),
    )
    json = Bool(
        False,
        config=True,
        help=(
            "If True, each line of output will be a JSON object with the "
            "details of the workspace."
        ),
    )

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the app."""
        super().initialize(*args, **kwargs)
        self.manager = WorkspacesManager(self.workspaces_dir)

    def start(self) -> None:
        """Start the app."""
        workspaces = self.manager.list_workspaces()
        if self.jsonlines:
            for workspace in workspaces:
                print(json.dumps(workspace))
        elif self.json:
            print(json.dumps(workspaces))
        else:
            for workspace in workspaces:
                print(workspace["metadata"]["id"])


class WorkspaceExportApp(JupyterApp, LabConfig):
    """A workspace export app."""

    version = __version__
    description = """
    Export a JupyterLab workspace

    If no arguments are passed in, this command will export the default
        workspace.
    If a workspace name is passed in, this command will export that workspace.
    If no workspace is found, this command will export an empty workspace.
    """

    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the app."""
        super().initialize(*args, **kwargs)
```
