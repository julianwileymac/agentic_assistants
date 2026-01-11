# Chunk: adb34eb6a0ca_0

- source: `.venv-lab/Lib/site-packages/IPython/utils/sysinfo.py`
- lines: 1-100
- chunk: 1/2

```
# encoding: utf-8
"""
Utilities for getting information about IPython and the system it's running in.
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os
import platform
import pprint
import sys
import subprocess

from pathlib import Path

from IPython.core import release
from IPython.utils import _sysinfo, encoding

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------

def pkg_commit_hash(pkg_path: str) -> tuple[str, str]:
    """Get short form of commit hash given directory `pkg_path`

    We get the commit hash from (in order of preference):

    * IPython.utils._sysinfo.commit
    * git output, if we are in a git repository

    If these fail, we return a not-found placeholder tuple

    Parameters
    ----------
    pkg_path : str
        directory containing package
        only used for getting commit from active repo

    Returns
    -------
    hash_from : str
        Where we got the hash from - description
    hash_str : str
        short form of hash
    """
    # Try and get commit from written commit text file
    if _sysinfo.commit:
        return "installation", _sysinfo.commit

    # maybe we are in a repository
    proc = subprocess.Popen('git rev-parse --short HEAD'.split(' '),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=pkg_path)
    repo_commit, _ = proc.communicate()
    if repo_commit:
        return 'repository', repo_commit.strip().decode('ascii')
    return '(none found)', '<not found>'


def pkg_info(pkg_path: str) -> dict:
    """Return dict describing the context of this package

    Parameters
    ----------
    pkg_path : str
        path containing __init__.py for package

    Returns
    -------
    context : dict
        with named parameters of interest
    """
    src, hsh = pkg_commit_hash(pkg_path)
    return dict(
        ipython_version=release.version,
        ipython_path=pkg_path,
        commit_source=src,
        commit_hash=hsh,
        sys_version=sys.version,
        sys_executable=sys.executable,
        sys_platform=sys.platform,
        platform=platform.platform(),
        os_name=os.name,
        default_encoding=encoding.DEFAULT_ENCODING,
        )

def get_sys_info() -> dict:
    """Return useful information about IPython and the system, as a dict."""
    path = Path(__file__, "..").resolve().parent
```
