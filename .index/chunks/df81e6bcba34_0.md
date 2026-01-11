# Chunk: df81e6bcba34_0

- source: `.venv-lab/Lib/site-packages/_distutils_hack/__init__.py`
- lines: 1-103
- chunk: 1/3

```
# don't import any costly modules
import os
import sys

report_url = (
    "https://github.com/pypa/setuptools/issues/new?template=distutils-deprecation.yml"
)


def warn_distutils_present():
    if 'distutils' not in sys.modules:
        return
    import warnings

    warnings.warn(
        "Distutils was imported before Setuptools, but importing Setuptools "
        "also replaces the `distutils` module in `sys.modules`. This may lead "
        "to undesirable behaviors or errors. To avoid these issues, avoid "
        "using distutils directly, ensure that setuptools is installed in the "
        "traditional way (e.g. not an editable install), and/or make sure "
        "that setuptools is always imported before distutils."
    )


def clear_distutils():
    if 'distutils' not in sys.modules:
        return
    import warnings

    warnings.warn(
        "Setuptools is replacing distutils. Support for replacing "
        "an already imported distutils is deprecated. In the future, "
        "this condition will fail. "
        f"Register concerns at {report_url}"
    )
    mods = [
        name
        for name in sys.modules
        if name == "distutils" or name.startswith("distutils.")
    ]
    for name in mods:
        del sys.modules[name]


def enabled():
    """
    Allow selection of distutils by environment variable.
    """
    which = os.environ.get('SETUPTOOLS_USE_DISTUTILS', 'local')
    if which == 'stdlib':
        import warnings

        warnings.warn(
            "Reliance on distutils from stdlib is deprecated. Users "
            "must rely on setuptools to provide the distutils module. "
            "Avoid importing distutils or import setuptools first, "
            "and avoid setting SETUPTOOLS_USE_DISTUTILS=stdlib. "
            f"Register concerns at {report_url}"
        )
    return which == 'local'


def ensure_local_distutils():
    import importlib

    clear_distutils()

    # With the DistutilsMetaFinder in place,
    # perform an import to cause distutils to be
    # loaded from setuptools._distutils. Ref #2906.
    with shim():
        importlib.import_module('distutils')

    # check that submodules load as expected
    core = importlib.import_module('distutils.core')
    assert '_distutils' in core.__file__, core.__file__
    assert 'setuptools._distutils.log' not in sys.modules


def do_override():
    """
    Ensure that the local copy of distutils is preferred over stdlib.

    See https://github.com/pypa/setuptools/issues/417#issuecomment-392298401
    for more motivation.
    """
    if enabled():
        warn_distutils_present()
        ensure_local_distutils()


class _TrivialRe:
    def __init__(self, *patterns) -> None:
        self._patterns = patterns

    def match(self, string):
        return all(pat in string for pat in self._patterns)


class DistutilsMetaFinder:
    def find_spec(self, fullname, path, target=None):
        # optimization: only consider top level modules and those
```
