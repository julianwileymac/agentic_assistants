# Chunk: 5d00beec3dbc_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/msilib/sequence.pyi`
- lines: 1-15
- chunk: 1/1

```
import sys
from typing import List, Optional, Tuple

if sys.platform == "win32":

    _SequenceType = List[Tuple[str, Optional[str], int]]

    AdminExecuteSequence: _SequenceType
    AdminUISequence: _SequenceType
    AdvtExecuteSequence: _SequenceType
    InstallExecuteSequence: _SequenceType
    InstallUISequence: _SequenceType

    tables: List[str]
```
