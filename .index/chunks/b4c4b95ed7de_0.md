# Chunk: b4c4b95ed7de_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/contrib/sites/management.pyi`
- lines: 1-14
- chunk: 1/1

```
from typing import Any

from django.apps.config import AppConfig
from django.apps.registry import Apps

def create_default_site(
    app_config: AppConfig,
    verbosity: int = ...,
    interactive: bool = ...,
    using: str = ...,
    apps: Apps = ...,
    **kwargs: Any
) -> None: ...
```
