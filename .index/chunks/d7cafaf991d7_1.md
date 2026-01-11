# Chunk: d7cafaf991d7_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 76-148
- chunk: 2/7

```
ion=None,
                           analysis_errors=True):
        """
        :param position: Position of the last statement -> tuple of line, column
        """
        if name_context is None:
            name_context = self
        names = self.goto(name_or_str, name_context, analysis_errors)
        values = ValueSet.from_sets(name.infer() for name in names)
        if not values:
            n = name_or_str.value if isinstance(name_or_str, Name) else name_or_str
            values = self.py__getattribute__alternatives(n)

        if not names and not values and analysis_errors:
            if isinstance(name_or_str, Name):
                from jedi.inference import analysis
                analysis.add_attribute_error(
                    name_context, self, name_or_str)
        debug.dbg('context.names_to_types: %s -> %s', names, values)
        return values

    def py__await__(self):
        await_value_set = self.py__getattribute__("__await__")
        if not await_value_set:
            debug.warning('Tried to run __await__ on value %s', self)
        return await_value_set.execute_with_values()

    def py__name__(self):
        return self.name.string_name

    def iterate(self, contextualized_node=None, is_async=False):
        debug.dbg('iterate %s', self)
        if is_async:
            from jedi.inference.lazy_value import LazyKnownValues
            # TODO if no __aiter__ values are there, error should be:
            # TypeError: 'async for' requires an object with __aiter__ method, got int
            return iter([
                LazyKnownValues(
                    self.py__getattribute__('__aiter__').execute_with_values()
                        .py__getattribute__('__anext__').execute_with_values()
                        .py__getattribute__('__await__').execute_with_values()
                        .py__stop_iteration_returns()
                )  # noqa: E124
            ])
        return self.py__iter__(contextualized_node)

    def is_sub_class_of(self, class_value):
        with debug.increase_indent_cm('subclass matching of %s <=> %s' % (self, class_value),
                                      color='BLUE'):
            for cls in self.py__mro__():
                if cls.is_same_class(class_value):
                    debug.dbg('matched subclass True', color='BLUE')
                    return True
            debug.dbg('matched subclass False', color='BLUE')
            return False

    def is_same_class(self, class2):
        # Class matching should prefer comparisons that are not this function.
        if type(class2).is_same_class != HelperValueMixin.is_same_class:
            return class2.is_same_class(self)
        return self == class2

    @memoize_method
    def as_context(self, *args, **kwargs):
        return self._as_context(*args, **kwargs)


class Value(HelperValueMixin):
    """
    To be implemented by subclasses.
    """
    tree_node = None
```
