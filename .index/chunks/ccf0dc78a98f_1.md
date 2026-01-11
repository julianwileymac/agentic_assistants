# Chunk: ccf0dc78a98f_1

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/tomli-2.0.1.dist-info/METADATA`
- lines: 66-156
- chunk: 2/4

```
>

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

with open("path_to_file/conf.toml", "rb") as f:
    toml_dict = tomli.load(f)
```

The file must be opened in binary mode (with the `"rb"` flag).
Binary mode will enforce decoding the file as UTF-8 with universal newlines disabled,
both of which are required to correctly parse TOML.

### Handle invalid TOML<a name="handle-invalid-toml"></a>

```python
import tomli

try:
    toml_dict = tomli.loads("]] this is invalid TOML [[")
except tomli.TOMLDecodeError:
    print("Yep, definitely not valid.")
```

Note that error messages are considered informational only.
They should not be assumed to stay constant across Tomli versions.

### Construct `decimal.Decimal`s from TOML floats<a name="construct-decimaldecimals-from-toml-floats"></a>

```python
from decimal import Decimal
import tomli

toml_dict = tomli.loads("precision-matters = 0.982492", parse_float=Decimal)
assert toml_dict["precision-matters"] == Decimal("0.982492")
```

Note that `decimal.Decimal` can be replaced with another callable that converts a TOML float from string to a Python type.
The `decimal.Decimal` is, however, a practical choice for use cases where float inaccuracies can not be tolerated.

Illegal types are `dict` and `list`, and their subtypes.
A `ValueError` will be raised if `parse_float` produces illegal types.

## FAQ<a name="faq"></a>

### Why this parser?<a name="why-this-parser"></a>

- it's lil'
- pure Python with zero dependencies
- the fastest pure Python parser [\*](#performance):
  15x as fast as [tomlkit](https://pypi.org/project/tomlkit/),
  2.4x as fast as [toml](https://pypi.org/project/toml/)
- outputs [basic data types](#how-do-toml-types-map-into-python-types) only
- 100% spec compliant: passes all tests in
  [a test set](https://github.com/toml-lang/compliance/pull/8)
  soon to be merged to the official
  [compliance tests for TOML](https://github.com/toml-lang/compliance)
  repository
- thoroughly tested: 100% branch coverage

### Is comment preserving round-trip parsing supported?<a name="is-comment-preserving-round-trip-parsing-supported"></a>

No.

The `tomli.loads` function returns a plain `dict` that is populated with builtin types and types from the standard library only.
Preserving comments requires a custom type to be returned so will not be supported,
at least not by the `tomli.loads` and `tomli.load` functions.

Look into [TOML Kit](https://github.com/sdispater/tomlkit) if preservation of style is what you need.

### Is there a `dumps`, `write` or `encode` function?<a name="is-there-a-dumps-write-or-encode-function"></a>

[Tomli-W](https://github.com/hukkin/tomli-w) is the write-only counterpart of Tomli, providing `dump` and `dumps` functions.
```
