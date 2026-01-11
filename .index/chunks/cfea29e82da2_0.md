# Chunk: cfea29e82da2_0

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/tests/unix_compat.py`
- lines: 1-18
- chunk: 1/1

```
import sys

try:
    import grp
    import pwd
except ImportError:
    grp = pwd = None

import pytest

UNIX_ID_SUPPORT = grp and pwd
UID_0_SUPPORT = UNIX_ID_SUPPORT and sys.platform != "cygwin"

require_unix_id = pytest.mark.skipif(
    not UNIX_ID_SUPPORT, reason="Requires grp and pwd support"
)
require_uid_0 = pytest.mark.skipif(not UID_0_SUPPORT, reason="Requires UID 0 support")
```
