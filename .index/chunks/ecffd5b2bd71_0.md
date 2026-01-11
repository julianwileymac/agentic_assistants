# Chunk: ecffd5b2bd71_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/template/loaders/locmem.pyi`
- lines: 1-12
- chunk: 1/1

```
from typing import Dict

from django.template.base import Origin
from django.template.engine import Engine

from .base import Loader as BaseLoader

class Loader(BaseLoader):
    templates_dict: Dict[str, str] = ...
    def __init__(self, engine: Engine, templates_dict: Dict[str, str]) -> None: ...
    def get_contents(self, origin: Origin) -> str: ...
```
