# Chunk: d4d3ef216dea_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/contrib/sessions/base_session.pyi`
- lines: 1-20
- chunk: 1/1

```
from datetime import datetime
from typing import Any, Dict, Optional, Type

from django.contrib.sessions.backends.base import SessionBase

from django.db import models

class BaseSessionManager(models.Manager):
    def encode(self, session_dict: Dict[str, int]) -> str: ...
    def save(self, session_key: str, session_dict: Dict[str, int], expire_date: datetime) -> AbstractBaseSession: ...

class AbstractBaseSession(models.Model):
    expire_date: datetime
    session_data: str
    session_key: str
    objects: Any = ...
    @classmethod
    def get_session_store_class(cls) -> Optional[Type[SessionBase]]: ...
    def get_decoded(self) -> Dict[str, int]: ...
```
