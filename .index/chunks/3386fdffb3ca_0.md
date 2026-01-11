# Chunk: 3386fdffb3ca_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/distutils/config.pyi`
- lines: 1-18
- chunk: 1/1

```
from abc import abstractmethod
from distutils.cmd import Command
from typing import ClassVar, List, Optional, Tuple

DEFAULT_PYPIRC: str

class PyPIRCCommand(Command):
    DEFAULT_REPOSITORY: ClassVar[str]
    DEFAULT_REALM: ClassVar[str]
    repository: None
    realm: None
    user_options: ClassVar[List[Tuple[str, Optional[str], str]]]
    boolean_options: ClassVar[List[str]]
    def initialize_options(self) -> None: ...
    def finalize_options(self) -> None: ...
    @abstractmethod
    def run(self) -> None: ...
```
