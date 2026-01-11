# Chunk: e6efc4eaf9c7_1

- source: `.venv-lab/Lib/site-packages/IPython/extensions/deduperreload/deduperreload_patching.py`
- lines: 86-148
- chunk: 2/2

```
e is NOT_FOUND:
            return
        elif old_value is new_value:
            return
        elif old_value is not None and offset < 0:
            offset = cls.infer_field_offset(old, field)
        elif offset < 0:
            assert not new_is_value
            assert new_value is not None
            offset = cls.infer_field_offset(new, field)
        cls.try_write_readonly_attr(old, field, new_value, offset=offset)

    @classmethod
    def try_patch_attr(
        cls,
        old: object,
        new: object,
        field: str,
        new_is_value: bool = False,
        offset: int = -1,
    ) -> None:
        try:
            setattr(old, field, new if new_is_value else getattr(new, field))
        except (AttributeError, TypeError, ValueError):
            cls.try_patch_readonly_attr(old, new, field, new_is_value, offset)

    @classmethod
    def patch_function(
        cls, to_patch_to: Any, to_patch_from: Any, is_method: bool
    ) -> None:
        new_closure = []
        for freevar, closure_val in zip(
            to_patch_from.__code__.co_freevars or [], to_patch_from.__closure__ or []
        ):
            if (
                callable(closure_val.cell_contents)
                and freevar in to_patch_to.__code__.co_freevars
            ):
                new_closure.append(
                    to_patch_to.__closure__[
                        to_patch_to.__code__.co_freevars.index(freevar)
                    ]
                )
            else:
                new_closure.append(closure_val)
        # lambdas may complain if there is more than one freevar
        cls.try_patch_attr(to_patch_to, to_patch_from, "__code__")
        offset = -1
        if to_patch_to.__closure__ is None and to_patch_from.__closure__ is not None:
            offset = cls.infer_field_offset(to_patch_from, "__closure__")
        if to_patch_to.__closure__ is not None or to_patch_from.__closure__ is not None:
            cls.try_patch_readonly_attr(
                to_patch_to,
                tuple(new_closure) or NULL,
                "__closure__",
                new_is_value=True,
                offset=offset,
            )
        for attr in ("__defaults__", "__kwdefaults__", "__doc__", "__dict__"):
            cls.try_patch_attr(to_patch_to, to_patch_from, attr)
        if is_method:
            cls.try_patch_readonly_attr(to_patch_to, to_patch_from, "__self__")
```
