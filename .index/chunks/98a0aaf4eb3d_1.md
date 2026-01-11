# Chunk: 98a0aaf4eb3d_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/_pydev_calltip_util.py`
- lines: 81-154
- chunk: 2/2

```
 create_class_stub(fn_class, fn_stub) + "\n" + expr
        else:
            expr = fn_name
            return fn_stub + "\n" + expr
    elif doc_string:
        if fn_name:
            restored_signature, _ = signature_from_docstring(doc_string, fn_name)
            if restored_signature:
                return create_method_stub(fn_name, fn_class, restored_signature, doc_string)
        return create_function_stub("unknown", "(*args, **kwargs)", doc_string) + "\nunknown"

    else:
        return ""


def get_docstring(obj):
    if obj is not None:
        try:
            if IS_JYTHON:
                # Jython
                doc = obj.__doc__
                if doc is not None:
                    return doc

                from _pydev_bundle import _pydev_jy_imports_tipper

                is_method, infos = _pydev_jy_imports_tipper.ismethod(obj)
                ret = ""
                if is_method:
                    for info in infos:
                        ret += info.get_as_doc()
                    return ret

            else:
                doc = inspect.getdoc(obj)
                if doc is not None:
                    return doc
        except:
            pass
    else:
        return ""
    try:
        # if no attempt succeeded, try to return repr()...
        return repr(obj)
    except:
        try:
            # otherwise the class
            return str(obj.__class__)
        except:
            # if all fails, go to an empty string
            return ""


def create_class_stub(class_name, contents):
    return "class %s(object):\n%s" % (class_name, contents)


def create_function_stub(fn_name, fn_argspec, fn_docstring, indent=0):
    def shift_right(string, prefix):
        return "".join(prefix + line for line in string.splitlines(True))

    fn_docstring = shift_right(inspect.cleandoc(fn_docstring), "  " * (indent + 1))
    ret = '''
def %s%s:
    """%s"""
    pass
''' % (fn_name, fn_argspec, fn_docstring)
    ret = ret[1:]  # remove first /n
    ret = ret.replace("\t", "  ")
    if indent:
        prefix = "  " * indent
        ret = shift_right(ret, prefix)
    return ret
```
