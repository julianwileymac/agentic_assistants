# Chunk: 98a0aaf4eb3d_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/_pydev_calltip_util.py`
- lines: 1-89
- chunk: 1/2

```
"""
License: Apache 2.0
Author: Yuli Fitterman
"""
import types

from _pydevd_bundle.pydevd_constants import IS_JYTHON

try:
    import inspect
except:
    import traceback

    traceback.print_exc()  # Ok, no inspect available (search will not work)

from _pydev_bundle._pydev_imports_tipper import signature_from_docstring


def is_bound_method(obj):
    if isinstance(obj, types.MethodType):
        return getattr(obj, "__self__", getattr(obj, "im_self", None)) is not None
    else:
        return False


def get_class_name(instance):
    return getattr(getattr(instance, "__class__", None), "__name__", None)


def get_bound_class_name(obj):
    my_self = getattr(obj, "__self__", getattr(obj, "im_self", None))
    if my_self is None:
        return None
    return get_class_name(my_self)


def get_description(obj):
    try:
        ob_call = obj.__call__
    except:
        ob_call = None

    if isinstance(obj, type) or type(obj).__name__ == "classobj":
        fob = getattr(obj, "__init__", lambda: None)
        if not isinstance(fob, (types.FunctionType, types.MethodType)):
            fob = obj
    elif is_bound_method(ob_call):
        fob = ob_call
    else:
        fob = obj

    argspec = ""
    fn_name = None
    fn_class = None
    if isinstance(fob, (types.FunctionType, types.MethodType)):
        spec_info = inspect.getfullargspec(fob)
        argspec = inspect.formatargspec(*spec_info)
        fn_name = getattr(fob, "__name__", None)
        if isinstance(obj, type) or type(obj).__name__ == "classobj":
            fn_name = "__init__"
            fn_class = getattr(obj, "__name__", "UnknownClass")
        elif is_bound_method(obj) or is_bound_method(ob_call):
            fn_class = get_bound_class_name(obj) or "UnknownClass"

    else:
        fn_name = getattr(fob, "__name__", None)
        fn_self = getattr(fob, "__self__", None)
        if fn_self is not None and not isinstance(fn_self, types.ModuleType):
            fn_class = get_class_name(fn_self)

    doc_string = get_docstring(ob_call) if is_bound_method(ob_call) else get_docstring(obj)
    return create_method_stub(fn_name, fn_class, argspec, doc_string)


def create_method_stub(fn_name, fn_class, argspec, doc_string):
    if fn_name and argspec:
        doc_string = "" if doc_string is None else doc_string
        fn_stub = create_function_stub(fn_name, argspec, doc_string, indent=1 if fn_class else 0)
        if fn_class:
            expr = fn_class if fn_name == "__init__" else fn_class + "()." + fn_name
            return create_class_stub(fn_class, fn_stub) + "\n" + expr
        else:
            expr = fn_name
            return fn_stub + "\n" + expr
    elif doc_string:
        if fn_name:
            restored_signature, _ = signature_from_docstring(doc_string, fn_name)
            if restored_signature:
```
