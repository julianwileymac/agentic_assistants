# Chunk: d7cafaf991d7_4

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 310-408
- chunk: 5/7

```
ions yield.
    """
    return ValueSet.from_sets(
        lazy_value.infer()
        for lazy_value in values.iterate(contextualized_node, is_async=is_async)
    )


class _ValueWrapperBase(HelperValueMixin):
    @safe_property
    def name(self):
        from jedi.inference.names import ValueName
        wrapped_name = self._wrapped_value.name
        if wrapped_name.tree_name is not None:
            return ValueName(self, wrapped_name.tree_name)
        else:
            from jedi.inference.compiled import CompiledValueName
            return CompiledValueName(self, wrapped_name.string_name)

    @classmethod
    @inference_state_as_method_param_cache()
    def create_cached(cls, inference_state, *args, **kwargs):
        return cls(*args, **kwargs)

    def __getattr__(self, name):
        assert name != '_wrapped_value', 'Problem with _get_wrapped_value'
        return getattr(self._wrapped_value, name)


class LazyValueWrapper(_ValueWrapperBase):
    @safe_property
    @memoize_method
    def _wrapped_value(self):
        with debug.increase_indent_cm('Resolve lazy value wrapper'):
            return self._get_wrapped_value()

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)

    def _get_wrapped_value(self):
        raise NotImplementedError


class ValueWrapper(_ValueWrapperBase):
    def __init__(self, wrapped_value):
        self._wrapped_value = wrapped_value

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._wrapped_value)


class TreeValue(Value):
    def __init__(self, inference_state, parent_context, tree_node):
        super().__init__(inference_state, parent_context)
        self.tree_node = tree_node

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.tree_node)


class ContextualizedNode:
    def __init__(self, context, node):
        self.context = context
        self.node = node

    def get_root_context(self):
        return self.context.get_root_context()

    def infer(self):
        return self.context.infer_node(self.node)

    def __repr__(self):
        return '<%s: %s in %s>' % (self.__class__.__name__, self.node, self.context)


def _getitem(value, index_values, contextualized_node):
    # The actual getitem call.
    result = NO_VALUES
    unused_values = set()
    for index_value in index_values:
        index = index_value.get_safe_value(default=None)
        if type(index) in (float, int, str, slice, bytes):
            try:
                result |= value.py__simple_getitem__(index)
                continue
            except SimpleGetItemNotFound:
                pass

        unused_values.add(index_value)

    # The index was somehow not good enough or simply a wrong type.
    # Therefore we now iterate through all the values and just take
    # all results.
    if unused_values or not index_values:
        result |= value.py__getitem__(
            ValueSet(unused_values),
            contextualized_node
        )
```
