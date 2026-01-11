# Chunk: d7cafaf991d7_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 134-242
- chunk: 3/7

```
ss:
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
    # Possible values: None, tuple, list, dict and set. Here to deal with these
    # very important containers.
    array_type = None
    api_type = 'not_defined_please_report_bug'

    def __init__(self, inference_state, parent_context=None):
        self.inference_state = inference_state
        self.parent_context = parent_context

    def py__getitem__(self, index_value_set, contextualized_node):
        from jedi.inference import analysis
        # TODO this value is probably not right.
        analysis.add(
            contextualized_node.context,
            'type-error-not-subscriptable',
            contextualized_node.node,
            message="TypeError: '%s' object is not subscriptable" % self
        )
        return NO_VALUES

    def py__simple_getitem__(self, index):
        raise SimpleGetItemNotFound

    def py__iter__(self, contextualized_node=None):
        if contextualized_node is not None:
            from jedi.inference import analysis
            analysis.add(
                contextualized_node.context,
                'type-error-not-iterable',
                contextualized_node.node,
                message="TypeError: '%s' object is not iterable" % self)
        return iter([])

    def py__next__(self, contextualized_node=None):
        return self.py__iter__(contextualized_node)

    def get_signatures(self):
        return []

    def is_class(self):
        return False

    def is_class_mixin(self):
        return False

    def is_instance(self):
        return False

    def is_function(self):
        return False

    def is_module(self):
        return False

    def is_namespace(self):
        return False

    def is_compiled(self):
        return False

    def is_bound_method(self):
        return False

    def is_builtins_module(self):
        return False

    def py__bool__(self):
        """
        Since Wrapper is a super class for classes, functions and modules,
        the return value will always be true.
        """
        return True

    def py__doc__(self):
        try:
            self.tree_node.get_doc_node
        except AttributeError:
            return ''
        else:
            return clean_scope_docstring(self.tree_node)

    def get_safe_value(self, default=sentinel):
        if default is sentinel:
            raise ValueError("There exists no safe value for value %s" % self)
        return default

    def execute_operation(self, other, operator):
        debug.warning("%s not possible between %s and %s", operator, self, other)
        return NO_VALUES

    def py__call__(self, arguments):
        debug.warning("no execution possible %s", self)
        return NO_VALUES
```
