# Chunk: ed6c86ea4d7d_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/sys.pyi`
- lines: 115-220
- chunk: 2/3

```
ash_info

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
    sizeof_digit: int

class _version_info(Tuple[int, int, int, str, int]):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int

version_info: _version_info

def call_tracing(__func: Callable[..., _T], __args: Any) -> _T: ...
def _clear_type_cache() -> None: ...
def _current_frames() -> Dict[int, Any]: ...
def _debugmallocstats() -> None: ...
def __displayhook__(value: object) -> None: ...
def __excepthook__(type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None: ...
def exc_info() -> _OptExcInfo: ...

# sys.exit() accepts an optional argument of anything printable
def exit(__status: object = ...) -> NoReturn: ...
def getdefaultencoding() -> str: ...

if sys.platform != "win32":
    def getdlopenflags() -> int: ...

def getfilesystemencoding() -> str: ...
def getfilesystemencodeerrors() -> str: ...
def getrefcount(__object: Any) -> int: ...
def getrecursionlimit() -> int: ...
@overload
def getsizeof(obj: object) -> int: ...
@overload
def getsizeof(obj: object, default: int) -> int: ...
def getswitchinterval() -> float: ...
def _getframe(__depth: int = ...) -> FrameType: ...

_ProfileFunc = Callable[[FrameType, str, Any], Any]

def getprofile() -> Optional[_ProfileFunc]: ...
def setprofile(profilefunc: Optional[_ProfileFunc]) -> None: ...

_TraceFunc = Callable[[FrameType, str, Any], Optional[Callable[[FrameType, str, Any], Any]]]

def gettrace() -> Optional[_TraceFunc]: ...
def settrace(tracefunc: Optional[_TraceFunc]) -> None: ...

class _WinVersion(Tuple[int, int, int, int, str, int, int, int, int, Tuple[int, int, int]]):
    major: int
    minor: int
    build: int
    platform: int
    service_pack: str
    service_pack_minor: int
    service_pack_major: int
    suite_mast: int
    product_type: int
    platform_version: Tuple[int, int, int]

if sys.platform == "win32":
    def getwindowsversion() -> _WinVersion: ...

def intern(__string: str) -> str: ...
def is_finalizing() -> bool: ...

if sys.version_info >= (3, 7):
    __breakpointhook__: Any  # contains the original value of breakpointhook
    def breakpointhook(*args: Any, **kwargs: Any) -> Any: ...

if sys.platform != "win32":
    def setdlopenflags(__flags: int) -> None: ...

def setrecursionlimit(__limit: int) -> None: ...
def setswitchinterval(__interval: float) -> None: ...
def gettotalrefcount() -> int: ...  # Debug builds only

if sys.version_info < (3, 9):
    def getcheckinterval() -> int: ...  # deprecated
    def setcheckinterval(__n: int) -> None: ...  # deprecated

if sys.version_info >= (3, 8):
    # not exported by sys
    class UnraisableHookArgs:
        exc_type: Type[BaseException]
```
