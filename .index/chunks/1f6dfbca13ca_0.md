# Chunk: 1f6dfbca13ca_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/contrib/messages/middleware.pyi`
- lines: 1-8
- chunk: 1/1

```
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class MessageMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> None: ...
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse: ...
```
