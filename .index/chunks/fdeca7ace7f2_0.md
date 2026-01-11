# Chunk: fdeca7ace7f2_0

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_distutils_adoption.py`
- lines: 1-105
- chunk: 1/3

```
import os
import platform
import sys
import textwrap

import pytest

IS_PYPY = '__pypy__' in sys.builtin_module_names

_TEXT_KWARGS = {"text": True, "encoding": "utf-8"}  # For subprocess.run


def win_sr(env):
    """
    On Windows, SYSTEMROOT must be present to avoid

    > Fatal Python error: _Py_HashRandomization_Init: failed to
    > get random numbers to initialize Python
    """
    if env and platform.system() == 'Windows':
        env['SYSTEMROOT'] = os.environ['SYSTEMROOT']
    return env


def find_distutils(venv, imports='distutils', env=None, **kwargs):
    py_cmd = 'import {imports}; print(distutils.__file__)'.format(**locals())
    cmd = ['python', '-c', py_cmd]
    return venv.run(cmd, env=win_sr(env), **_TEXT_KWARGS, **kwargs)


def count_meta_path(venv, env=None):
    py_cmd = textwrap.dedent(
        """
        import sys
        is_distutils = lambda finder: finder.__class__.__name__ == "DistutilsMetaFinder"
        print(len(list(filter(is_distutils, sys.meta_path))))
        """
    )
    cmd = ['python', '-c', py_cmd]
    return int(venv.run(cmd, env=win_sr(env), **_TEXT_KWARGS))


skip_without_stdlib_distutils = pytest.mark.skipif(
    sys.version_info >= (3, 12),
    reason='stdlib distutils is removed from Python 3.12+',
)


@skip_without_stdlib_distutils
def test_distutils_stdlib(venv):
    """
    Ensure stdlib distutils is used when appropriate.
    """
    env = dict(SETUPTOOLS_USE_DISTUTILS='stdlib')
    assert venv.name not in find_distutils(venv, env=env).split(os.sep)
    assert count_meta_path(venv, env=env) == 0


def test_distutils_local_with_setuptools(venv):
    """
    Ensure local distutils is used when appropriate.
    """
    env = dict(SETUPTOOLS_USE_DISTUTILS='local')
    loc = find_distutils(venv, imports='setuptools, distutils', env=env)
    assert venv.name in loc.split(os.sep)
    assert count_meta_path(venv, env=env) <= 1


@pytest.mark.xfail('IS_PYPY', reason='pypy imports distutils on startup')
def test_distutils_local(venv):
    """
    Even without importing, the setuptools-local copy of distutils is
    preferred.
    """
    env = dict(SETUPTOOLS_USE_DISTUTILS='local')
    assert venv.name in find_distutils(venv, env=env).split(os.sep)
    assert count_meta_path(venv, env=env) <= 1


def test_pip_import(venv):
    """
    Ensure pip can be imported.
    Regression test for #3002.
    """
    cmd = ['python', '-c', 'import pip']
    venv.run(cmd, **_TEXT_KWARGS)


def test_distutils_has_origin():
    """
    Distutils module spec should have an origin. #2990.
    """
    assert __import__('distutils').__spec__.origin


ENSURE_IMPORTS_ARE_NOT_DUPLICATED = r"""
# Depending on the importlib machinery and _distutils_hack, some imports are
# duplicated resulting in different module objects being loaded, which prevents
# patches as shown in #3042.
# This script provides a way of verifying if this duplication is happening.

from distutils import cmd
import distutils.command.sdist as sdist
```
