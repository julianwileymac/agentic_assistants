# Chunk: ccf0dc78a98f_0

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/tomli-2.0.1.dist-info/METADATA`
- lines: 1-87
- chunk: 1/4

```
Metadata-Version: 2.1
Name: tomli
Version: 2.0.1
Summary: A lil' TOML parser
Keywords: toml
Author-email: Taneli Hukkinen <hukkin@users.noreply.github.com>
Requires-Python: >=3.7
Description-Content-Type: text/markdown
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: MacOS
Classifier: Operating System :: Microsoft :: Windows
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: Python :: 3 :: Only
Classifier: Programming Language :: Python :: 3.7
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: 3.9
Classifier: Programming Language :: Python :: 3.10
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Typing :: Typed
Project-URL: Changelog, https://github.com/hukkin/tomli/blob/master/CHANGELOG.md
Project-URL: Homepage, https://github.com/hukkin/tomli

[![Build Status](https://github.com/hukkin/tomli/workflows/Tests/badge.svg?branch=master)](https://github.com/hukkin/tomli/actions?query=workflow%3ATests+branch%3Amaster+event%3Apush)
[![codecov.io](https://codecov.io/gh/hukkin/tomli/branch/master/graph/badge.svg)](https://codecov.io/gh/hukkin/tomli)
[![PyPI version](https://img.shields.io/pypi/v/tomli)](https://pypi.org/project/tomli)

# Tomli

> A lil' TOML parser

**Table of Contents**  *generated with [mdformat-toc](https://github.com/hukkin/mdformat-toc)*

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Intro](#intro)
- [Installation](#installation)
- [Usage](#usage)
  - [Parse a TOML string](#parse-a-toml-string)
  - [Parse a TOML file](#parse-a-toml-file)
  - [Handle invalid TOML](#handle-invalid-toml)
  - [Construct `decimal.Decimal`s from TOML floats](#construct-decimaldecimals-from-toml-floats)
- [FAQ](#faq)
  - [Why this parser?](#why-this-parser)
  - [Is comment preserving round-trip parsing supported?](#is-comment-preserving-round-trip-parsing-supported)
  - [Is there a `dumps`, `write` or `encode` function?](#is-there-a-dumps-write-or-encode-function)
  - [How do TOML types map into Python types?](#how-do-toml-types-map-into-python-types)
- [Performance](#performance)

<!-- mdformat-toc end -->

## Intro<a name="intro"></a>

Tomli is a Python library for parsing [TOML](https://toml.io).
Tomli is fully compatible with [TOML v1.0.0](https://toml.io/en/v1.0.0).

## Installation<a name="installation"></a>

```bash
pip install tomli
```

## Usage<a name="usage"></a>

### Parse a TOML string<a name="parse-a-toml-string"></a>

```python
import tomli

toml_str = """
           gretzky = 99

           [kurri]
           jari = 17
           """

toml_dict = tomli.loads(toml_str)
assert toml_dict == {"gretzky": 99, "kurri": {"jari": 17}}
```

### Parse a TOML file<a name="parse-a-toml-file"></a>

```python
import tomli
```
