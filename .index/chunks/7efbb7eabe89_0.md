# Chunk: 7efbb7eabe89_0

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/licenses_handler.py`
- lines: 1-87
- chunk: 1/4

```
"""Manager and Tornado handlers for license reporting."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import asyncio
import csv
import io
import json
import mimetypes
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jupyter_server.base.handlers import APIHandler
from tornado import web
from traitlets import List, Unicode
from traitlets.config import LoggingConfigurable

from .config import get_federated_extensions

# this is duplicated in @juptyerlab/builder
DEFAULT_THIRD_PARTY_LICENSE_FILE = "third-party-licenses.json"
UNKNOWN_PACKAGE_NAME = "UNKNOWN"

if mimetypes.guess_extension("text/markdown") is None:  # pragma: no cover
    # for python <3.8 https://bugs.python.org/issue39324
    mimetypes.add_type("text/markdown", ".md")


class LicensesManager(LoggingConfigurable):
    """A manager for listing the licenses for all frontend end code distributed
    by an application and any federated extensions
    """

    executor = ThreadPoolExecutor(max_workers=1)

    third_party_licenses_files = List(
        Unicode(),
        default_value=[
            DEFAULT_THIRD_PARTY_LICENSE_FILE,
            f"static/{DEFAULT_THIRD_PARTY_LICENSE_FILE}",
        ],
        help="the license report data in built app and federated extensions",
    )

    @property
    def federated_extensions(self) -> dict[str, Any]:
        """Lazily load the currrently-available federated extensions.

        This is expensive, but probably the only way to be sure to get
        up-to-date license information for extensions installed interactively.
        """
        if TYPE_CHECKING:
            from .app import LabServerApp

            assert isinstance(self.parent, LabServerApp)

        per_paths = [
            self.parent.labextensions_path,
            self.parent.extra_labextensions_path,
        ]
        labextensions_path = [extension for extensions in per_paths for extension in extensions]
        return get_federated_extensions(labextensions_path)

    async def report_async(
        self, report_format: str = "markdown", bundles_pattern: str = ".*", full_text: bool = False
    ) -> tuple[str, str]:
        """Asynchronous wrapper around the potentially slow job of locating
        and encoding all of the licenses
        """
        return await asyncio.wrap_future(
            self.executor.submit(
                self.report,
                report_format=report_format,
                bundles_pattern=bundles_pattern,
                full_text=full_text,
            )
        )

    def report(self, report_format: str, bundles_pattern: str, full_text: bool) -> tuple[str, str]:
        """create a human- or machine-readable report"""
        bundles = self.bundles(bundles_pattern=bundles_pattern)
        if report_format == "json":
```
