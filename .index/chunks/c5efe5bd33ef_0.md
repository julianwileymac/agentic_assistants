# Chunk: c5efe5bd33ef_0

- source: `.venv-lab/Lib/site-packages/jupyter_server/base/handlers.py`
- lines: 1-96
- chunk: 1/17

```
"""Base Tornado handlers for the Jupyter server."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import functools
import inspect
import ipaddress
import json
import mimetypes
import os
import re
import types
import warnings
from collections.abc import Awaitable, Coroutine, Sequence
from http.client import responses
from logging import Logger
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlparse

import prometheus_client
from jinja2 import TemplateNotFound
from jupyter_core.paths import is_hidden
from tornado import web
from tornado.log import app_log
from traitlets.config import Application

import jupyter_server
from jupyter_server import CallContext
from jupyter_server._sysinfo import get_sys_info
from jupyter_server._tz import utcnow
from jupyter_server.auth.decorator import allow_unauthenticated, authorized
from jupyter_server.auth.identity import User
from jupyter_server.i18n import combine_translations
from jupyter_server.services.security import csp_report_uri
from jupyter_server.utils import (
    ensure_async,
    filefind,
    url_escape,
    url_is_absolute,
    url_path_join,
    urldecode_unix_socket_path,
)

if TYPE_CHECKING:
    from jupyter_client.kernelspec import KernelSpecManager
    from jupyter_events import EventLogger
    from jupyter_server_terminals.terminalmanager import TerminalManager
    from tornado.concurrent import Future

    from jupyter_server.auth.authorizer import Authorizer
    from jupyter_server.auth.identity import IdentityProvider
    from jupyter_server.serverapp import ServerApp
    from jupyter_server.services.config.manager import ConfigManager
    from jupyter_server.services.contents.manager import ContentsManager
    from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager
    from jupyter_server.services.sessions.sessionmanager import SessionManager

# -----------------------------------------------------------------------------
# Top-level handlers
# -----------------------------------------------------------------------------

_sys_info_cache = None


def json_sys_info():
    """Get sys info as json."""
    global _sys_info_cache  # noqa: PLW0603
    if _sys_info_cache is None:
        _sys_info_cache = json.dumps(get_sys_info())
    return _sys_info_cache


def log() -> Logger:
    """Get the application log."""
    if Application.initialized():
        return cast(Logger, Application.instance().log)
    else:
        return app_log


class AuthenticatedHandler(web.RequestHandler):
    """A RequestHandler with an authenticated user."""

    @property
    def base_url(self) -> str:
        return cast(str, self.settings.get("base_url", "/"))

    @property
    def content_security_policy(self) -> str:
        """The default Content-Security-Policy header

        Can be overridden by defining Content-Security-Policy in settings['headers']
        """
```
