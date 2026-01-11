# Chunk: 9e31eca8a6cf_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/os/__init__.pyi`
- lines: 1-121
- chunk: 1/5

```
import sys
from _typeshed import AnyPath, FileDescriptorLike
from builtins import OSError
from io import TextIOWrapper as _TextIOWrapper
from posix import listdir as listdir, stat_result as stat_result  # TODO: use this, see https://github.com/python/mypy/issues/3078
from typing import (
    IO,
    Any,
    AnyStr,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NamedTuple,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Text,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from . import path as path

# We need to use something from path, or flake8 and pytype get unhappy
_supports_unicode_filenames = path.supports_unicode_filenames

_T = TypeVar("_T")

# ----- os variables -----

error = OSError

if sys.version_info >= (3, 2):
    supports_bytes_environ: bool

if sys.version_info >= (3, 3):
    supports_dir_fd: Set[Callable[..., Any]]
    supports_fd: Set[Callable[..., Any]]
    supports_effective_ids: Set[Callable[..., Any]]
    supports_follow_symlinks: Set[Callable[..., Any]]

SEEK_SET: int
SEEK_CUR: int
SEEK_END: int

O_RDONLY: int
O_WRONLY: int
O_RDWR: int
O_APPEND: int
O_CREAT: int
O_EXCL: int
O_TRUNC: int
# We don't use sys.platform for O_* flags to denote platform-dependent APIs because some codes,
# including tests for mypy, use a more finer way than sys.platform before using these APIs
# See https://github.com/python/typeshed/pull/2286 for discussions
O_DSYNC: int  # Unix only
O_RSYNC: int  # Unix only
O_SYNC: int  # Unix only
O_NDELAY: int  # Unix only
O_NONBLOCK: int  # Unix only
O_NOCTTY: int  # Unix only
O_SHLOCK: int  # Unix only
O_EXLOCK: int  # Unix only
O_BINARY: int  # Windows only
O_NOINHERIT: int  # Windows only
O_SHORT_LIVED: int  # Windows only
O_TEMPORARY: int  # Windows only
O_RANDOM: int  # Windows only
O_SEQUENTIAL: int  # Windows only
O_TEXT: int  # Windows only
O_ASYNC: int  # Gnu extension if in C library
O_DIRECT: int  # Gnu extension if in C library
O_DIRECTORY: int  # Gnu extension if in C library
O_NOFOLLOW: int  # Gnu extension if in C library
O_NOATIME: int  # Gnu extension if in C library
O_LARGEFILE: int  # Gnu extension if in C library

curdir: str
pardir: str
sep: str
if sys.platform == "win32":
    altsep: str
else:
    altsep: Optional[str]
extsep: str
pathsep: str
defpath: str
linesep: str
devnull: str
name: str

F_OK: int
R_OK: int
W_OK: int
X_OK: int

class _Environ(MutableMapping[AnyStr, AnyStr], Generic[AnyStr]):
    def copy(self) -> Dict[AnyStr, AnyStr]: ...
    def __delitem__(self, key: AnyStr) -> None: ...
    def __getitem__(self, key: AnyStr) -> AnyStr: ...
    def __setitem__(self, key: AnyStr, value: AnyStr) -> None: ...
    def __iter__(self) -> Iterator[AnyStr]: ...
    def __len__(self) -> int: ...

environ: _Environ[str]
if sys.version_info >= (3, 2):
    environb: _Environ[bytes]

if sys.platform != "win32":
    # Unix only
    confstr_names: Dict[str, int]
    pathconf_names: Dict[str, int]
    sysconf_names: Dict[str, int]
```
