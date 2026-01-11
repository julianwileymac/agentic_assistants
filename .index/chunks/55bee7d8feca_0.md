# Chunk: 55bee7d8feca_0

- source: `.venv-lab/Lib/site-packages/ipykernel-7.1.0.dist-info/METADATA`
- lines: 1-77
- chunk: 1/2

```
Metadata-Version: 2.4
Name: ipykernel
Version: 7.1.0
Summary: IPython Kernel for Jupyter
Project-URL: Homepage, https://ipython.org
Project-URL: Documentation, https://ipykernel.readthedocs.io
Project-URL: Source, https://github.com/ipython/ipykernel
Project-URL: Tracker, https://github.com/ipython/ipykernel/issues
Author-email: IPython Development Team <ipython-dev@scipy.org>
License-Expression: BSD-3-Clause
License-File: LICENSE
Keywords: Interactive,Interpreter,Shell,Web
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Science/Research
Classifier: Intended Audience :: System Administrators
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 3
Requires-Python: >=3.10
Requires-Dist: appnope>=0.1.2; platform_system == 'Darwin'
Requires-Dist: comm>=0.1.1
Requires-Dist: debugpy>=1.6.5
Requires-Dist: ipython>=7.23.1
Requires-Dist: jupyter-client>=8.0.0
Requires-Dist: jupyter-core!=5.0.*,>=4.12
Requires-Dist: matplotlib-inline>=0.1
Requires-Dist: nest-asyncio>=1.4
Requires-Dist: packaging>=22
Requires-Dist: psutil>=5.7
Requires-Dist: pyzmq>=25
Requires-Dist: tornado>=6.2
Requires-Dist: traitlets>=5.4.0
Provides-Extra: cov
Requires-Dist: coverage[toml]; extra == 'cov'
Requires-Dist: matplotlib; extra == 'cov'
Requires-Dist: pytest-cov; extra == 'cov'
Requires-Dist: trio; extra == 'cov'
Provides-Extra: docs
Requires-Dist: intersphinx-registry; extra == 'docs'
Requires-Dist: myst-parser; extra == 'docs'
Requires-Dist: pydata-sphinx-theme; extra == 'docs'
Requires-Dist: sphinx-autodoc-typehints; extra == 'docs'
Requires-Dist: sphinx<8.2.0; extra == 'docs'
Requires-Dist: sphinxcontrib-github-alt; extra == 'docs'
Requires-Dist: sphinxcontrib-spelling; extra == 'docs'
Requires-Dist: trio; extra == 'docs'
Provides-Extra: pyqt5
Requires-Dist: pyqt5; extra == 'pyqt5'
Provides-Extra: pyside6
Requires-Dist: pyside6; extra == 'pyside6'
Provides-Extra: test
Requires-Dist: flaky; extra == 'test'
Requires-Dist: ipyparallel; extra == 'test'
Requires-Dist: pre-commit; extra == 'test'
Requires-Dist: pytest-asyncio>=0.23.5; extra == 'test'
Requires-Dist: pytest-cov; extra == 'test'
Requires-Dist: pytest-timeout; extra == 'test'
Requires-Dist: pytest<9,>=7.0; extra == 'test'
Description-Content-Type: text/markdown

# IPython Kernel for Jupyter

[![Build Status](https://github.com/ipython/ipykernel/actions/workflows/ci.yml/badge.svg?query=branch%3Amain++)](https://github.com/ipython/ipykernel/actions/workflows/ci.yml/badge.svg?query=branch%3Amain++)
[![Documentation Status](https://readthedocs.org/projects/ipykernel/badge/?version=latest)](http://ipykernel.readthedocs.io/en/latest/?badge=latest)

This package provides the IPython kernel for Jupyter.

## Installation from source

1. `git clone`
1. `cd ipykernel`
1. `pip install -e ".[test]"`

After that, all normal `ipython` commands will use this newly-installed version of the kernel.

## Running tests
```
