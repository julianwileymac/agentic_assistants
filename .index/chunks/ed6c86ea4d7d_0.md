# Chunk: ed6c86ea4d7d_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/sys.pyi`
- lines: 1-136
- chunk: 1/3

```
import sys
from builtins import object as _object
from importlib.abc import MetaPathFinder, PathEntryFinder
from types import FrameType, ModuleType, TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

_T = TypeVar("_T")

# The following type alias are stub-only and do not exist during runtime
_ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
_OptExcInfo = Union[_ExcInfo, Tuple[None, None, None]]

# ----- sys variables -----
if sys.platform != "win32":
    abiflags: str
argv: List[str]
base_exec_prefix: str
base_prefix: str
byteorder: str
builtin_module_names: Sequence[str]  # actually a tuple of strings
copyright: str
if sys.platform == "win32":
    dllhandle: int
dont_write_bytecode: bool
displayhook: Callable[[object], Any]
excepthook: Callable[[Type[BaseException], BaseException, TracebackType], Any]
exec_prefix: str
executable: str
float_repr_style: str
hexversion: int
last_type: Optional[Type[BaseException]]
last_value: Optional[BaseException]
last_traceback: Optional[TracebackType]
maxsize: int
maxunicode: int
meta_path: List[MetaPathFinder]
modules: Dict[str, ModuleType]
path: List[str]
path_hooks: List[Any]  # TODO precise type; function, path to finder
path_importer_cache: Dict[str, Optional[PathEntryFinder]]
platform: str
if sys.version_info >= (3, 9):
    platlibdir: str
prefix: str
if sys.version_info >= (3, 8):
    pycache_prefix: Optional[str]
ps1: str
ps2: str
stdin: TextIO
stdout: TextIO
stderr: TextIO
__stdin__: TextIO
__stdout__: TextIO
__stderr__: TextIO
tracebacklimit: int
version: str
api_version: int
warnoptions: Any
#  Each entry is a tuple of the form (action, message, category, module,
#    lineno)
if sys.platform == "win32":
    winver: str
_xoptions: Dict[Any, Any]

flags: _flags

class _flags:
    debug: int
    division_warning: int
    inspect: int
    interactive: int
    optimize: int
    dont_write_bytecode: int
    no_user_site: int
    no_site: int
    ignore_environment: int
    verbose: int
    bytes_warning: int
    quiet: int
    hash_randomization: int
    if sys.version_info >= (3, 7):
        dev_mode: int
        utf8_mode: int

float_info: _float_info

class _float_info:
    epsilon: float  # DBL_EPSILON
    dig: int  # DBL_DIG
    mant_dig: int  # DBL_MANT_DIG
    max: float  # DBL_MAX
    max_exp: int  # DBL_MAX_EXP
    max_10_exp: int  # DBL_MAX_10_EXP
    min: float  # DBL_MIN
    min_exp: int  # DBL_MIN_EXP
    min_10_exp: int  # DBL_MIN_10_EXP
    radix: int  # FLT_RADIX
    rounds: int  # FLT_ROUNDS

hash_info: _hash_info

class _hash_info:
    width: int
    modulus: int
    inf: int
    nan: int
    imag: int

implementation: _implementation

class _implementation:
    name: str
    version: _version_info
    hexversion: int
    cache_tag: str

int_info: _int_info

class _int_info:
    bits_per_digit: int
```
