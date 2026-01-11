# Chunk: fe3edd72ff72_0

- source: `.venv-lab/Lib/site-packages/nbconvert/exporters/webpdf.py`
- lines: 1-95
- chunk: 1/3

```
"""Export to PDF via a headless browser"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import concurrent.futures
import os
import subprocess
import sys
import tempfile
from importlib import util as importlib_util

from traitlets import Bool, default

from .html import HTMLExporter

PLAYWRIGHT_INSTALLED = importlib_util.find_spec("playwright") is not None
IS_WINDOWS = os.name == "nt"


class WebPDFExporter(HTMLExporter):
    """Writer designed to write to PDF files.

    This inherits from :class:`HTMLExporter`. It creates the HTML using the
    template machinery, and then run playwright to create a pdf.
    """

    export_from_notebook = "PDF via HTML"

    allow_chromium_download = Bool(
        False,
        help="Whether to allow downloading Chromium if no suitable version is found on the system.",
    ).tag(config=True)

    paginate = Bool(
        True,
        help="""
        Split generated notebook into multiple pages.

        If False, a PDF with one long page will be generated.

        Set to True to match behavior of LaTeX based PDF generator
        """,
    ).tag(config=True)

    @default("file_extension")
    def _file_extension_default(self):
        return ".html"

    @default("template_name")
    def _template_name_default(self):
        return "webpdf"

    disable_sandbox = Bool(
        False,
        help="""
        Disable chromium security sandbox when converting to PDF.

        WARNING: This could cause arbitrary code execution in specific circumstances,
        where JS in your notebook can execute serverside code! Please use with
        caution.

        ``https://github.com/puppeteer/puppeteer/blob/main@%7B2020-12-14T17:22:24Z%7D/docs/troubleshooting.md#setting-up-chrome-linux-sandbox``
        has more information.

        This is required for webpdf to work inside most container environments.
        """,
    ).tag(config=True)

    def run_playwright(self, html):
        """Run playwright."""

        async def main(temp_file):
            """Run main playwright script."""
            args = ["--no-sandbox"] if self.disable_sandbox else []
            try:
                from playwright.async_api import async_playwright  # type: ignore[import-not-found]
            except ModuleNotFoundError as e:
                msg = (
                    "Playwright is not installed to support Web PDF conversion. "
                    "Please install `nbconvert[webpdf]` to enable."
                )
                raise RuntimeError(msg) from e

            if self.allow_chromium_download:
                cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
                subprocess.check_call(cmd)  # noqa: S603

            playwright = await async_playwright().start()
            chromium = playwright.chromium

            try:
                browser = await chromium.launch(
```
