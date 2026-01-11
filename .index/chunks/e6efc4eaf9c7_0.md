# Chunk: e6efc4eaf9c7_0

- source: `.venv-lab/Lib/site-packages/IPython/extensions/deduperreload/deduperreload_patching.py`
- lines: 1-95
- chunk: 1/2

```
from __future__ import annotations
import ctypes
import sys
from typing import Any

NOT_FOUND: object = object()
NULL: object = object()
_MAX_FIELD_SEARCH_OFFSET = 50

if sys.maxsize > 2**32:
    WORD_TYPE: type[ctypes.c_int32] | type[ctypes.c_int64] = ctypes.c_int64
    WORD_N_BYTES = 8
else:
    WORD_TYPE = ctypes.c_int32
    WORD_N_BYTES = 4


class DeduperReloaderPatchingMixin:
    @staticmethod
    def infer_field_offset(
        obj: object,
        field: str,
    ) -> int:
        field_value = getattr(obj, field, NOT_FOUND)
        if field_value is NOT_FOUND:
            return -1
        obj_addr = ctypes.c_void_p.from_buffer(ctypes.py_object(obj)).value
        field_addr = ctypes.c_void_p.from_buffer(ctypes.py_object(field_value)).value
        if obj_addr is None or field_addr is None:
            return -1
        ret = -1
        for offset in range(1, _MAX_FIELD_SEARCH_OFFSET):
            if (
                ctypes.cast(
                    obj_addr + WORD_N_BYTES * offset, ctypes.POINTER(WORD_TYPE)
                ).contents.value
                == field_addr
            ):
                ret = offset
                break
        return ret

    @classmethod
    def try_write_readonly_attr(
        cls,
        obj: object,
        field: str,
        new_value: object,
        offset: int | None = None,
    ) -> None:
        prev_value = getattr(obj, field, NOT_FOUND)
        if prev_value is NOT_FOUND:
            return
        if offset is None:
            offset = cls.infer_field_offset(obj, field)
        if offset == -1:
            return
        obj_addr = ctypes.c_void_p.from_buffer(ctypes.py_object(obj)).value
        if new_value is NULL:
            new_value_addr: int | None = 0
        else:
            new_value_addr = ctypes.c_void_p.from_buffer(
                ctypes.py_object(new_value)
            ).value
        if obj_addr is None or new_value_addr is None:
            return
        if prev_value is not None:
            ctypes.pythonapi.Py_DecRef(ctypes.py_object(prev_value))
        if new_value not in (None, NULL):
            ctypes.pythonapi.Py_IncRef(ctypes.py_object(new_value))
        ctypes.cast(
            obj_addr + WORD_N_BYTES * offset, ctypes.POINTER(WORD_TYPE)
        ).contents.value = new_value_addr

    @classmethod
    def try_patch_readonly_attr(
        cls,
        old: object,
        new: object,
        field: str,
        new_is_value: bool = False,
        offset: int = -1,
    ) -> None:
        old_value = getattr(old, field, NOT_FOUND)
        new_value = new if new_is_value else getattr(new, field, NOT_FOUND)
        if old_value is NOT_FOUND or new_value is NOT_FOUND:
            return
        elif old_value is new_value:
            return
        elif old_value is not None and offset < 0:
            offset = cls.infer_field_offset(old, field)
        elif offset < 0:
            assert not new_is_value
            assert new_value is not None
```
