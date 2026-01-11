# Chunk: e370edcf8fd5_3

- source: `.venv-lab/Lib/site-packages/jedi/inference/filters.py`
- lines: 231-323
- chunk: 4/5

```
 = dct

    def get(self, name):
        try:
            value = self._convert(name, self._dct[name])
        except KeyError:
            return []
        else:
            return list(self._filter([value]))

    def values(self):
        def yielder():
            for item in self._dct.items():
                try:
                    yield self._convert(*item)
                except KeyError:
                    pass
        return self._filter(yielder())

    def _convert(self, name, value):
        return value

    def __repr__(self):
        keys = ', '.join(self._dct.keys())
        return '<%s: for {%s}>' % (self.__class__.__name__, keys)


class MergedFilter:
    def __init__(self, *filters):
        self._filters = filters

    def get(self, name):
        return [n for filter in self._filters for n in filter.get(name)]

    def values(self):
        return [n for filter in self._filters for n in filter.values()]

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(str(f) for f in self._filters))


class _BuiltinMappedMethod(ValueWrapper):
    """``Generator.__next__`` ``dict.values`` methods and so on."""
    api_type = 'function'

    def __init__(self, value, method, builtin_func):
        super().__init__(builtin_func)
        self._value = value
        self._method = method

    def py__call__(self, arguments):
        # TODO add TypeError if params are given/or not correct.
        return self._method(self._value, arguments)


class SpecialMethodFilter(DictFilter):
    """
    A filter for methods that are defined in this module on the corresponding
    classes like Generator (for __next__, etc).
    """
    class SpecialMethodName(AbstractNameDefinition):
        api_type = 'function'

        def __init__(self, parent_context, string_name, callable_, builtin_value):
            self.parent_context = parent_context
            self.string_name = string_name
            self._callable = callable_
            self._builtin_value = builtin_value

        def infer(self):
            for filter in self._builtin_value.get_filters():
                # We can take the first index, because on builtin methods there's
                # always only going to be one name. The same is true for the
                # inferred values.
                for name in filter.get(self.string_name):
                    builtin_func = next(iter(name.infer()))
                    break
                else:
                    continue
                break
            return ValueSet([
                _BuiltinMappedMethod(self.parent_context, self._callable, builtin_func)
            ])

    def __init__(self, value, dct, builtin_value):
        super().__init__(dct)
        self.value = value
        self._builtin_value = builtin_value
        """
        This value is what will be used to introspect the name, where as the
        other value will be used to execute the function.
```
