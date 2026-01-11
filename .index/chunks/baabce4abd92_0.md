# Chunk: baabce4abd92_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/email/mime/text.pyi`
- lines: 1-9
- chunk: 1/1

```
from email.mime.nonmultipart import MIMENonMultipart
from email.policy import Policy
from typing import Optional

class MIMEText(MIMENonMultipart):
    def __init__(
        self, _text: str, _subtype: str = ..., _charset: Optional[str] = ..., *, policy: Optional[Policy] = ...
    ) -> None: ...
```
