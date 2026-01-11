# Chunk: aca4d71eac9b_0

- source: `.venv-lab/Lib/site-packages/jupyterlab/tests/mock_packages/extension/setup.py`
- lines: 1-16
- chunk: 1/1

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os.path as osp

name = "mock-package"
HERE = osp.abspath(osp.dirname(__file__))

with open(osp.join(HERE, "package.json")) as fid:
    data = json.load(fid)

from setuptools import setup  # noqa

setup(name=name, version=data["version"], py_modules=[name])
```
