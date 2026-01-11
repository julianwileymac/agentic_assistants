# Chunk: fdeca7ace7f2_1

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_distutils_adoption.py`
- lines: 97-189
- chunk: 2/3

```
achinery and _distutils_hack, some imports are
# duplicated resulting in different module objects being loaded, which prevents
# patches as shown in #3042.
# This script provides a way of verifying if this duplication is happening.

from distutils import cmd
import distutils.command.sdist as sdist

# import last to prevent caching
from distutils import {imported_module}

for mod in (cmd, sdist):
    assert mod.{imported_module} == {imported_module}, (
        f"\n{{mod.dir_util}}\n!=\n{{{imported_module}}}"
    )

print("success")
"""


@pytest.mark.usefixtures("tmpdir_cwd")
@pytest.mark.parametrize(
    ('distutils_version', 'imported_module'),
    [
        pytest.param("stdlib", "dir_util", marks=skip_without_stdlib_distutils),
        pytest.param("stdlib", "file_util", marks=skip_without_stdlib_distutils),
        pytest.param("stdlib", "archive_util", marks=skip_without_stdlib_distutils),
        ("local", "dir_util"),
        ("local", "file_util"),
        ("local", "archive_util"),
    ],
)
def test_modules_are_not_duplicated_on_import(distutils_version, imported_module, venv):
    env = dict(SETUPTOOLS_USE_DISTUTILS=distutils_version)
    script = ENSURE_IMPORTS_ARE_NOT_DUPLICATED.format(imported_module=imported_module)
    cmd = ['python', '-c', script]
    output = venv.run(cmd, env=win_sr(env), **_TEXT_KWARGS).strip()
    assert output == "success"


ENSURE_LOG_IMPORT_IS_NOT_DUPLICATED = r"""
import types
import distutils.dist as dist
from distutils import log
if isinstance(dist.log, types.ModuleType):
    assert dist.log == log, f"\n{dist.log}\n!=\n{log}"
print("success")
"""


@pytest.mark.usefixtures("tmpdir_cwd")
@pytest.mark.parametrize(
    "distutils_version",
    [
        "local",
        pytest.param("stdlib", marks=skip_without_stdlib_distutils),
    ],
)
def test_log_module_is_not_duplicated_on_import(distutils_version, venv):
    env = dict(SETUPTOOLS_USE_DISTUTILS=distutils_version)
    cmd = ['python', '-c', ENSURE_LOG_IMPORT_IS_NOT_DUPLICATED]
    output = venv.run(cmd, env=win_sr(env), **_TEXT_KWARGS).strip()
    assert output == "success"


ENSURE_CONSISTENT_ERROR_FROM_MODIFIED_PY = r"""
from setuptools.modified import newer
from {imported_module}.errors import DistutilsError

# Can't use pytest.raises in this context
try:
    newer("", "")
except DistutilsError:
    print("success")
else:
    raise AssertionError("Expected to raise")
"""


@pytest.mark.usefixtures("tmpdir_cwd")
@pytest.mark.parametrize(
    ('distutils_version', 'imported_module'),
    [
        ("local", "distutils"),
        # Unfortunately we still get ._distutils.errors.DistutilsError with SETUPTOOLS_USE_DISTUTILS=stdlib
        # But that's a deprecated use-case we don't mind not fully supporting in newer code
        pytest.param(
            "stdlib", "setuptools._distutils", marks=skip_without_stdlib_distutils
        ),
    ],
)
def test_consistent_error_from_modified_py(distutils_version, imported_module, venv):
```
