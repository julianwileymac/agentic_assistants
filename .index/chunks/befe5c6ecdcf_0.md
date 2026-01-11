# Chunk: befe5c6ecdcf_0

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 1-83
- chunk: 1/12

```
from __future__ import annotations

import functools
import logging
import os
import shutil
import sys
import uuid
import zipfile
from collections.abc import Collection, Iterable
from optparse import Values
from pathlib import Path
from typing import Any

from pip._vendor.packaging.markers import Marker
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.specifiers import SpecifierSet
from pip._vendor.packaging.utils import canonicalize_name
from pip._vendor.packaging.version import Version
from pip._vendor.packaging.version import parse as parse_version
from pip._vendor.pyproject_hooks import BuildBackendHookCaller

from pip._internal.build_env import BuildEnvironment, NoOpBuildEnvironment
from pip._internal.exceptions import InstallationError, PreviousBuildDirError
from pip._internal.locations import get_scheme
from pip._internal.metadata import (
    BaseDistribution,
    get_default_environment,
    get_directory_distribution,
    get_wheel_distribution,
)
from pip._internal.metadata.base import FilesystemWheel
from pip._internal.models.direct_url import DirectUrl
from pip._internal.models.link import Link
from pip._internal.operations.build.metadata import generate_metadata
from pip._internal.operations.build.metadata_editable import generate_editable_metadata
from pip._internal.operations.install.wheel import install_wheel
from pip._internal.pyproject import load_pyproject_toml, make_pyproject_path
from pip._internal.req.req_uninstall import UninstallPathSet
from pip._internal.utils.deprecation import deprecated
from pip._internal.utils.hashes import Hashes
from pip._internal.utils.misc import (
    ConfiguredBuildBackendHookCaller,
    ask_path_exists,
    backup_dir,
    display_path,
    hide_url,
    is_installable_dir,
    redact_auth_from_requirement,
    redact_auth_from_url,
)
from pip._internal.utils.packaging import get_requirement
from pip._internal.utils.subprocess import runner_with_spinner_message
from pip._internal.utils.temp_dir import TempDirectory, tempdir_kinds
from pip._internal.utils.unpacking import unpack_file
from pip._internal.utils.virtualenv import running_under_virtualenv
from pip._internal.vcs import vcs

logger = logging.getLogger(__name__)


class InstallRequirement:
    """
    Represents something that may be installed later on, may have information
    about where to fetch the relevant requirement and also contains logic for
    installing the said requirement.
    """

    def __init__(
        self,
        req: Requirement | None,
        comes_from: str | InstallRequirement | None,
        editable: bool = False,
        link: Link | None = None,
        markers: Marker | None = None,
        isolated: bool = False,
        *,
        hash_options: dict[str, list[str]] | None = None,
        config_settings: dict[str, str | list[str]] | None = None,
        constraint: bool = False,
        extras: Collection[str] = (),
        user_supplied: bool = False,
```
