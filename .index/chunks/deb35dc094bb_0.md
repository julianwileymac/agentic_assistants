# Chunk: deb35dc094bb_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/contrib/staticfiles/templatetags/staticfiles.pyi`
- lines: 1-10
- chunk: 1/1

```
from typing import Any

from django.template.base import Parser, Token
from django.templatetags.static import StaticNode

register: Any

def static(path: str) -> str: ...
def do_static(parser: Parser, token: Token) -> StaticNode: ...
```
