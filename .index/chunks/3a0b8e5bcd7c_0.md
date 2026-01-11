# Chunk: 3a0b8e5bcd7c_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/xmlrpc/server.pyi`
- lines: 1-68
- chunk: 1/3

```
import http.server
import pydoc
import socketserver
import sys
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Pattern, Protocol, Tuple, Type, Union
from xmlrpc.client import Fault

_Marshallable = Union[
    None, bool, int, float, str, bytes, tuple, list, dict, datetime
]  # TODO: Recursive type on tuple, list, dict

# The dispatch accepts anywhere from 0 to N arguments, no easy way to allow this in mypy
class _DispatchArity0(Protocol):
    def __call__(self) -> _Marshallable: ...

class _DispatchArity1(Protocol):
    def __call__(self, __arg1: _Marshallable) -> _Marshallable: ...

class _DispatchArity2(Protocol):
    def __call__(self, __arg1: _Marshallable, __arg2: _Marshallable) -> _Marshallable: ...

class _DispatchArity3(Protocol):
    def __call__(self, __arg1: _Marshallable, __arg2: _Marshallable, __arg3: _Marshallable) -> _Marshallable: ...

class _DispatchArity4(Protocol):
    def __call__(
        self, __arg1: _Marshallable, __arg2: _Marshallable, __arg3: _Marshallable, __arg4: _Marshallable
    ) -> _Marshallable: ...

class _DispatchArityN(Protocol):
    def __call__(self, *args: _Marshallable) -> _Marshallable: ...

_DispatchProtocol = Union[_DispatchArity0, _DispatchArity1, _DispatchArity2, _DispatchArity3, _DispatchArity4, _DispatchArityN]

def resolve_dotted_attribute(obj: Any, attr: str, allow_dotted_names: bool = ...) -> Any: ...  # undocumented
def list_public_methods(obj: Any) -> List[str]: ...  # undocumented

class SimpleXMLRPCDispatcher:  # undocumented

    funcs: Dict[str, _DispatchProtocol]
    instance: Optional[Any]
    allow_none: bool
    encoding: str
    use_builtin_types: bool
    def __init__(self, allow_none: bool = ..., encoding: Optional[str] = ..., use_builtin_types: bool = ...) -> None: ...
    def register_instance(self, instance: Any, allow_dotted_names: bool = ...) -> None: ...
    if sys.version_info >= (3, 7):
        def register_function(
            self, function: Optional[_DispatchProtocol] = ..., name: Optional[str] = ...
        ) -> Callable[..., Any]: ...
    else:
        def register_function(self, function: _DispatchProtocol, name: Optional[str] = ...) -> Callable[..., Any]: ...
    def register_introspection_functions(self) -> None: ...
    def register_multicall_functions(self) -> None: ...
    def _marshaled_dispatch(
        self,
        data: str,
        dispatch_method: Optional[
            Callable[[Optional[str], Tuple[_Marshallable, ...]], Union[Fault, Tuple[_Marshallable, ...]]]
        ] = ...,
        path: Optional[Any] = ...,
    ) -> str: ...  # undocumented
    def system_listMethods(self) -> List[str]: ...  # undocumented
    def system_methodSignature(self, method_name: str) -> str: ...  # undocumented
    def system_methodHelp(self, method_name: str) -> str: ...  # undocumented
    def system_multicall(self, call_list: List[Dict[str, _Marshallable]]) -> List[_Marshallable]: ...  # undocumented
```
