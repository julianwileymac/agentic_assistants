# Chunk: ccf0dc78a98f_2

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/tomli-2.0.1.dist-info/METADATA`
- lines: 150-193
- chunk: 3/4

```
sdispater/tomlkit) if preservation of style is what you need.

### Is there a `dumps`, `write` or `encode` function?<a name="is-there-a-dumps-write-or-encode-function"></a>

[Tomli-W](https://github.com/hukkin/tomli-w) is the write-only counterpart of Tomli, providing `dump` and `dumps` functions.

The core library does not include write capability, as most TOML use cases are read-only, and Tomli intends to be minimal.

### How do TOML types map into Python types?<a name="how-do-toml-types-map-into-python-types"></a>

| TOML type        | Python type         | Details                                                      |
| ---------------- | ------------------- | ------------------------------------------------------------ |
| Document Root    | `dict`              |                                                              |
| Key              | `str`               |                                                              |
| String           | `str`               |                                                              |
| Integer          | `int`               |                                                              |
| Float            | `float`             |                                                              |
| Boolean          | `bool`              |                                                              |
| Offset Date-Time | `datetime.datetime` | `tzinfo` attribute set to an instance of `datetime.timezone` |
| Local Date-Time  | `datetime.datetime` | `tzinfo` attribute set to `None`                             |
| Local Date       | `datetime.date`     |                                                              |
| Local Time       | `datetime.time`     |                                                              |
| Array            | `list`              |                                                              |
| Table            | `dict`              |                                                              |
| Inline Table     | `dict`              |                                                              |

## Performance<a name="performance"></a>

The `benchmark/` folder in this repository contains a performance benchmark for comparing the various Python TOML parsers.
The benchmark can be run with `tox -e benchmark-pypi`.
Running the benchmark on my personal computer output the following:

```console
foo@bar:~/dev/tomli$ tox -e benchmark-pypi
benchmark-pypi installed: attrs==19.3.0,click==7.1.2,pytomlpp==1.0.2,qtoml==0.3.0,rtoml==0.7.0,toml==0.10.2,tomli==1.1.0,tomlkit==0.7.2
benchmark-pypi run-test-pre: PYTHONHASHSEED='2658546909'
benchmark-pypi run-test: commands[0] | python -c 'import datetime; print(datetime.date.today())'
2021-07-23
benchmark-pypi run-test: commands[1] | python --version
Python 3.8.10
benchmark-pypi run-test: commands[2] | python benchmark/run.py
Parsing data.toml 5000 times:
------------------------------------------------------
```
