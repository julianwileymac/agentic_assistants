# Chunk: d41d90eff3fc_0

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 1-99
- chunk: 1/8

```
"""
Utilities for file-based Contents/Checkpoints managers.
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import annotations

import errno
import hashlib
import os
import shutil
from base64 import decodebytes, encodebytes
from contextlib import contextmanager
from functools import partial

import nbformat
from anyio.to_thread import run_sync
from tornado.web import HTTPError
from traitlets import Bool, Enum
from traitlets.config import Configurable
from traitlets.config.configurable import LoggingConfigurable

from jupyter_server.utils import ApiPath, to_api_path, to_os_path


def replace_file(src, dst):
    """replace dst with src"""
    os.replace(src, dst)


async def async_replace_file(src, dst):
    """replace dst with src asynchronously"""
    await run_sync(os.replace, src, dst)


def copy2_safe(src, dst, log=None):
    """copy src to dst

    like shutil.copy2, but log errors in copystat instead of raising
    """
    # if src file is not writable, avoid creating a back-up
    if not os.access(src, os.W_OK):
        if log:
            log.debug("Source file, %s, is not writable", src, exc_info=True)
        raise PermissionError(errno.EACCES, f"File is not writable: {src}")

    shutil.copyfile(src, dst)
    try:
        shutil.copystat(src, dst)
    except OSError:
        if log:
            log.debug("copystat on %s failed", dst, exc_info=True)


async def async_copy2_safe(src, dst, log=None):
    """copy src to dst asynchronously

    like shutil.copy2, but log errors in copystat instead of raising
    """
    if not os.access(src, os.W_OK):
        if log:
            log.debug("Source file, %s, is not writable", src, exc_info=True)
        raise PermissionError(errno.EACCES, f"File is not writable: {src}")

    await run_sync(shutil.copyfile, src, dst)
    try:
        await run_sync(shutil.copystat, src, dst)
    except OSError:
        if log:
            log.debug("copystat on %s failed", dst, exc_info=True)


def path_to_intermediate(path):
    """Name of the intermediate file used in atomic writes.

    The .~ prefix will make Dropbox ignore the temporary file."""
    dirname, basename = os.path.split(path)
    return os.path.join(dirname, ".~" + basename)


def path_to_invalid(path):
    """Name of invalid file after a failed atomic write and subsequent read."""
    dirname, basename = os.path.split(path)
    return os.path.join(dirname, basename + ".invalid")


@contextmanager
def atomic_writing(path, text=True, encoding="utf-8", log=None, **kwargs):
    """Context manager to write to a file only if the entire write is successful.

    This works by copying the previous file contents to a temporary file in the
    same directory, and renaming that file back to the target if the context
    exits with an error. If the context is successful, the new data is synced to
    disk and the temporary file is removed.

    Parameters
    ----------
```
