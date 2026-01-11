# Chunk: 2ac4d72dae1c_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/types.pyi`
- lines: 1-113
- chunk: 1/4

```
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)
from typing_extensions import Literal, final

# ModuleType is exported from this module, but for circular import
# reasons exists in its own stub file (with ModuleSpec and Loader).
from _importlib_modulespec import ModuleType as ModuleType  # Exported

# Note, all classes "defined" here require special handling.

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

class _Cell:
    cell_contents: Any

class FunctionType:
    __closure__: Optional[Tuple[_Cell, ...]]
    __code__: CodeType
    __defaults__: Optional[Tuple[Any, ...]]
    __dict__: Dict[str, Any]
    __globals__: Dict[str, Any]
    __name__: str
    __qualname__: str
    __annotations__: Dict[str, Any]
    __kwdefaults__: Dict[str, Any]
    def __init__(
        self,
        code: CodeType,
        globals: Dict[str, Any],
        name: Optional[str] = ...,
        argdefs: Optional[Tuple[object, ...]] = ...,
        closure: Optional[Tuple[_Cell, ...]] = ...,
    ) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
    def __get__(self, obj: Optional[object], type: Optional[type]) -> MethodType: ...

LambdaType = FunctionType

class CodeType:
    """Create a code object.  Not for the faint of heart."""

    co_argcount: int
    if sys.version_info >= (3, 8):
        co_posonlyargcount: int
    co_kwonlyargcount: int
    co_nlocals: int
    co_stacksize: int
    co_flags: int
    co_code: bytes
    co_consts: Tuple[Any, ...]
    co_names: Tuple[str, ...]
    co_varnames: Tuple[str, ...]
    co_filename: str
    co_name: str
    co_firstlineno: int
    co_lnotab: bytes
    co_freevars: Tuple[str, ...]
    co_cellvars: Tuple[str, ...]
    if sys.version_info >= (3, 8):
        def __init__(
            self,
            argcount: int,
            posonlyargcount: int,
            kwonlyargcount: int,
            nlocals: int,
            stacksize: int,
            flags: int,
            codestring: bytes,
            constants: Tuple[Any, ...],
            names: Tuple[str, ...],
            varnames: Tuple[str, ...],
            filename: str,
            name: str,
            firstlineno: int,
            lnotab: bytes,
            freevars: Tuple[str, ...] = ...,
            cellvars: Tuple[str, ...] = ...,
        ) -> None: ...
    else:
        def __init__(
            self,
            argcount: int,
            kwonlyargcount: int,
            nlocals: int,
            stacksize: int,
            flags: int,
            codestring: bytes,
            constants: Tuple[Any, ...],
            names: Tuple[str, ...],
            varnames: Tuple[str, ...],
            filename: str,
            name: str,
            firstlineno: int,
```
