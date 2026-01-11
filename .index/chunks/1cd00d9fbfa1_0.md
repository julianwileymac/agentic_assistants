# Chunk: 1cd00d9fbfa1_0

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/req_command.py`
- lines: 1-86
- chunk: 1/6

```
"""Contains the RequirementCommand base class.

This class is in a separate module so the commands that do not always
need PackageFinder capability don't unnecessarily import the
PackageFinder machinery and all its vendored dependencies, etc.
"""

from __future__ import annotations

import logging
import os
from functools import partial
from optparse import Values
from typing import Any, Callable, TypeVar

from pip._internal.build_env import SubprocessBuildEnvironmentInstaller
from pip._internal.cache import WheelCache
from pip._internal.cli import cmdoptions
from pip._internal.cli.index_command import IndexGroupCommand
from pip._internal.cli.index_command import SessionCommandMixin as SessionCommandMixin
from pip._internal.exceptions import CommandError, PreviousBuildDirError
from pip._internal.index.collector import LinkCollector
from pip._internal.index.package_finder import PackageFinder
from pip._internal.models.selection_prefs import SelectionPreferences
from pip._internal.models.target_python import TargetPython
from pip._internal.network.session import PipSession
from pip._internal.operations.build.build_tracker import BuildTracker
from pip._internal.operations.prepare import RequirementPreparer
from pip._internal.req.constructors import (
    install_req_from_editable,
    install_req_from_line,
    install_req_from_parsed_requirement,
    install_req_from_req_string,
)
from pip._internal.req.req_dependency_group import parse_dependency_groups
from pip._internal.req.req_file import parse_requirements
from pip._internal.req.req_install import InstallRequirement
from pip._internal.resolution.base import BaseResolver
from pip._internal.utils.temp_dir import (
    TempDirectory,
    TempDirectoryTypeRegistry,
    tempdir_kinds,
)

logger = logging.getLogger(__name__)


def should_ignore_regular_constraints(options: Values) -> bool:
    """
    Check if regular constraints should be ignored because
    we are in a isolated build process and build constraints
    feature is enabled but no build constraints were passed.
    """

    return os.environ.get("_PIP_IN_BUILD_IGNORE_CONSTRAINTS") == "1"


KEEPABLE_TEMPDIR_TYPES = [
    tempdir_kinds.BUILD_ENV,
    tempdir_kinds.EPHEM_WHEEL_CACHE,
    tempdir_kinds.REQ_BUILD,
]


_CommandT = TypeVar("_CommandT", bound="RequirementCommand")


def with_cleanup(
    func: Callable[[_CommandT, Values, list[str]], int],
) -> Callable[[_CommandT, Values, list[str]], int]:
    """Decorator for common logic related to managing temporary
    directories.
    """

    def configure_tempdir_registry(registry: TempDirectoryTypeRegistry) -> None:
        for t in KEEPABLE_TEMPDIR_TYPES:
            registry.set_delete(t, False)

    def wrapper(self: _CommandT, options: Values, args: list[str]) -> int:
        assert self.tempdir_registry is not None
        if options.no_clean:
            configure_tempdir_registry(self.tempdir_registry)

        try:
            return func(self, options, args)
```
