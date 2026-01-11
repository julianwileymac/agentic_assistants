# Chunk: a179a3ecb1bf_0

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 1-114
- chunk: 1/45

```
from __future__ import annotations

# Use of this source code is governed by the MIT license.
__license__ = "MIT"

import re
import warnings

from bs4.css import CSS
from bs4._deprecation import (
    _deprecated,
    _deprecated_alias,
    _deprecated_function_alias,
)
from bs4.formatter import (
    Formatter,
    HTMLFormatter,
    XMLFormatter,
)
from bs4._warnings import AttributeResemblesVariableWarning

from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableSequence,
    Optional,
    Pattern,
    Set,
    TYPE_CHECKING,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from typing_extensions import (
    Self,
    TypeAlias,
)

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.builder import TreeBuilder
    from bs4.filter import ElementFilter
    from bs4.formatter import (
        _EntitySubstitutionFunction,
        _FormatterOrName,
    )
    from bs4._typing import (
        _AtMostOneElement,
        _AtMostOneTag,
        _AtMostOneNavigableString,
        _AttributeValue,
        _AttributeValues,
        _Encoding,
        _InsertableElement,
        _OneElement,
        _QueryResults,
        _RawOrProcessedAttributeValues,
        _StrainableElement,
        _StrainableAttribute,
        _StrainableAttributes,
        _StrainableString,
        _SomeNavigableStrings,
        _SomeTags,
    )

_OneOrMoreStringTypes: TypeAlias = Union[
    Type["NavigableString"], Iterable[Type["NavigableString"]]
]

_FindMethodName: TypeAlias = Optional[Union["_StrainableElement", "ElementFilter"]]

# Deprecated module-level attributes.
# See https://peps.python.org/pep-0562/
_deprecated_names = dict(
    whitespace_re="The {name} attribute was deprecated in version 4.7.0. If you need it, make your own copy."
)
#: :meta private:
_deprecated_whitespace_re: Pattern[str] = re.compile(r"\s+")


def __getattr__(name: str) -> Any:
    if name in _deprecated_names:
        message = _deprecated_names[name]
        warnings.warn(message.format(name=name), DeprecationWarning, stacklevel=2)

        return globals()[f"_deprecated_{name}"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


#: Documents output by Beautiful Soup will be encoded with
#: this encoding unless you specify otherwise.
DEFAULT_OUTPUT_ENCODING: str = "utf-8"

#: A regular expression that can be used to split on whitespace.
nonwhitespace_re: Pattern[str] = re.compile(r"\S+")

#: These encodings are recognized by Python (so `Tag.encode`
#: could theoretically support them) but XML and HTML don't recognize
#: them (so they should not show up in an XML or HTML document as that
#: document's encoding).
#:
#: If an XML document is encoded in one of these encodings, no encoding
#: will be mentioned in the XML declaration. If an HTML document is
#: encoded in one of these encodings, and the HTML document has a
```
