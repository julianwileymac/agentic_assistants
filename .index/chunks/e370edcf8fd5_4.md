# Chunk: e370edcf8fd5_4

- source: `.venv-lab/Lib/site-packages/jedi/inference/filters.py`
- lines: 315-372
- chunk: 5/5

```
    def __init__(self, value, dct, builtin_value):
        super().__init__(dct)
        self.value = value
        self._builtin_value = builtin_value
        """
        This value is what will be used to introspect the name, where as the
        other value will be used to execute the function.

        We distinguish, because we have to.
        """

    def _convert(self, name, value):
        return self.SpecialMethodName(self.value, name, value, self._builtin_value)


class _OverwriteMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        base_dct = {}
        for base_cls in reversed(cls.__bases__):
            try:
                base_dct.update(base_cls.overwritten_methods)
            except AttributeError:
                pass

        for func in cls.__dict__.values():
            try:
                base_dct.update(func.registered_overwritten_methods)
            except AttributeError:
                pass
        cls.overwritten_methods = base_dct


class _AttributeOverwriteMixin:
    def get_filters(self, *args, **kwargs):
        yield SpecialMethodFilter(self, self.overwritten_methods, self._wrapped_value)
        yield from self._wrapped_value.get_filters(*args, **kwargs)


class LazyAttributeOverwrite(_AttributeOverwriteMixin, LazyValueWrapper,
                             metaclass=_OverwriteMeta):
    def __init__(self, inference_state):
        self.inference_state = inference_state


class AttributeOverwrite(_AttributeOverwriteMixin, ValueWrapper,
                         metaclass=_OverwriteMeta):
    pass


def publish_method(method_name):
    def decorator(func):
        dct = func.__dict__.setdefault('registered_overwritten_methods', {})
        dct[method_name] = func
        return func
    return decorator
```
