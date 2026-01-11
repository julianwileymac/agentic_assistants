# Chunk: 7ca6b73bc9ff_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/contrib/redirects/middleware.pyi`
- lines: 1-11
- chunk: 1/1

```
from typing import Any

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class RedirectFallbackMiddleware(MiddlewareMixin):
    response_gone_class: Any = ...
    response_redirect_class: Any = ...
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse: ...
```
