# Chunk: baa9be2beba8_0

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/importlib_metadata/compat/py311.py`
- lines: 1-23
- chunk: 1/1

```
import os
import pathlib
import sys
import types


def wrap(path):  # pragma: no cover
    """
    Workaround for https://github.com/python/cpython/issues/84538
    to add backward compatibility for walk_up=True.
    An example affected package is dask-labextension, which uses
    jupyter-packaging to install JupyterLab javascript files outside
    of site-packages.
    """

    def relative_to(root, *, walk_up=False):
        return pathlib.Path(os.path.relpath(path, root))

    return types.SimpleNamespace(relative_to=relative_to)


relative_fix = wrap if sys.version_info < (3, 12) else lambda x: x
```
