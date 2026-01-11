# Chunk: faf8ce6b523f_0

- source: `.venv-lab/Lib/site-packages/IPython/core/profiledir.py`
- lines: 1-83
- chunk: 1/4

```
# encoding: utf-8
"""An object for managing IPython profile directories."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import shutil
import errno
from pathlib import Path

from traitlets.config.configurable import LoggingConfigurable
from ..paths import get_ipython_package_dir
from ..utils.path import expand_path, ensure_dir_exists
from traitlets import Unicode, Bool, observe

from typing import Optional

#-----------------------------------------------------------------------------
# Module errors
#-----------------------------------------------------------------------------

class ProfileDirError(Exception):
    pass


#-----------------------------------------------------------------------------
# Class for managing profile directories
#-----------------------------------------------------------------------------

class ProfileDir(LoggingConfigurable):
    """An object to manage the profile directory and its resources.

    The profile directory is used by all IPython applications, to manage
    configuration, logging and security.

    This object knows how to find, create and manage these directories. This
    should be used by any code that wants to handle profiles.
    """

    security_dir_name = Unicode('security')
    log_dir_name = Unicode('log')
    startup_dir_name = Unicode('startup')
    pid_dir_name = Unicode('pid')
    static_dir_name = Unicode('static')
    security_dir = Unicode(u'')
    log_dir = Unicode(u'')
    startup_dir = Unicode(u'')
    pid_dir = Unicode(u'')
    static_dir = Unicode(u'')

    location = Unicode(u'',
        help="""Set the profile location directly. This overrides the logic used by the
        `profile` option.""",
        ).tag(config=True)

    _location_isset = Bool(False) # flag for detecting multiply set location
    @observe('location')
    def _location_changed(self, change):
        if self._location_isset:
            raise RuntimeError("Cannot set profile location more than once.")
        self._location_isset = True
        new = change['new']
        ensure_dir_exists(new)

        # ensure config files exist:
        self.security_dir = os.path.join(new, self.security_dir_name)
        self.log_dir = os.path.join(new, self.log_dir_name)
        self.startup_dir = os.path.join(new, self.startup_dir_name)
        self.pid_dir = os.path.join(new, self.pid_dir_name)
        self.static_dir = os.path.join(new, self.static_dir_name)
        self.check_dirs()

    def _mkdir(self, path: str, mode: Optional[int] = None) -> bool:
        """ensure a directory exists at a given path

        This is a version of os.mkdir, with the following differences:

        - returns whether the directory has been created or not.
        - ignores EEXIST, protecting against race conditions where
          the dir may have been created in between the check and
          the creation
```
