# Chunk: bfa76c21e5af_0

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/typeguard/_decorators.py`
- lines: 1-84
- chunk: 1/4

```
from __future__ import annotations

import ast
import inspect
import sys
from collections.abc import Sequence
from functools import partial
from inspect import isclass, isfunction
from types import CodeType, FrameType, FunctionType
from typing import TYPE_CHECKING, Any, Callable, ForwardRef, TypeVar, cast, overload
from warnings import warn

from ._config import CollectionCheckStrategy, ForwardRefPolicy, global_config
from ._exceptions import InstrumentationWarning
from ._functions import TypeCheckFailCallback
from ._transformer import TypeguardTransformer
from ._utils import Unset, function_name, get_stacklevel, is_method_of, unset

if TYPE_CHECKING:
    from typeshed.stdlib.types import _Cell

    _F = TypeVar("_F")

    def typeguard_ignore(f: _F) -> _F:
        """This decorator is a noop during static type-checking."""
        return f

else:
    from typing import no_type_check as typeguard_ignore  # noqa: F401

T_CallableOrType = TypeVar("T_CallableOrType", bound=Callable[..., Any])


def make_cell(value: object) -> _Cell:
    return (lambda: value).__closure__[0]  # type: ignore[index]


def find_target_function(
    new_code: CodeType, target_path: Sequence[str], firstlineno: int
) -> CodeType | None:
    target_name = target_path[0]
    for const in new_code.co_consts:
        if isinstance(const, CodeType):
            if const.co_name == target_name:
                if const.co_firstlineno == firstlineno:
                    return const
                elif len(target_path) > 1:
                    target_code = find_target_function(
                        const, target_path[1:], firstlineno
                    )
                    if target_code:
                        return target_code

    return None


def instrument(f: T_CallableOrType) -> FunctionType | str:
    if not getattr(f, "__code__", None):
        return "no code associated"
    elif not getattr(f, "__module__", None):
        return "__module__ attribute is not set"
    elif f.__code__.co_filename == "<stdin>":
        return "cannot instrument functions defined in a REPL"
    elif hasattr(f, "__wrapped__"):
        return (
            "@typechecked only supports instrumenting functions wrapped with "
            "@classmethod, @staticmethod or @property"
        )

    target_path = [item for item in f.__qualname__.split(".") if item != "<locals>"]
    module_source = inspect.getsource(sys.modules[f.__module__])
    module_ast = ast.parse(module_source)
    instrumentor = TypeguardTransformer(target_path, f.__code__.co_firstlineno)
    instrumentor.visit(module_ast)

    if not instrumentor.target_node or instrumentor.target_lineno is None:
        return "instrumentor did not find the target function"

    module_code = compile(module_ast, f.__code__.co_filename, "exec", dont_inherit=True)
    new_code = find_target_function(
        module_code, target_path, instrumentor.target_lineno
    )
    if not new_code:
```
