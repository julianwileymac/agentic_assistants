# Chunk: ade6fb9dcfdc_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/markupsafe/_speedups.pyi`
- lines: 1-9
- chunk: 1/1

```
from typing import Text, Union

from . import Markup
from ._compat import text_type

def escape(s: Union[Markup, Text]) -> Markup: ...
def escape_silent(s: Union[None, Markup, Text]) -> Markup: ...
def soft_unicode(s: Text) -> text_type: ...
```
