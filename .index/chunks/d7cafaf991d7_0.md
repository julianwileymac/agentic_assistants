# Chunk: d7cafaf991d7_0

- source: `.venv-lab/Lib/site-packages/jedi/inference/base_value.py`
- lines: 1-84
- chunk: 1/7

```
"""
Values are the "values" that Python would return. However Values are at the
same time also the "values" that a user is currently sitting in.

A ValueSet is typically used to specify the return of a function or any other
static analysis operation. In jedi there are always multiple returns and not
just one.
"""
from functools import reduce
from operator import add
from itertools import zip_longest

from parso.python.tree import Name

from jedi import debug
from jedi.parser_utils import clean_scope_docstring
from jedi.inference.helpers import SimpleGetItemNotFound
from jedi.inference.utils import safe_property
from jedi.inference.cache import inference_state_as_method_param_cache
from jedi.cache import memoize_method

sentinel = object()


class HasNoContext(Exception):
    pass


class HelperValueMixin:
    def get_root_context(self):
        value = self
        if value.parent_context is None:
            return value.as_context()

        while True:
            if value.parent_context is None:
                return value
            value = value.parent_context

    def execute(self, arguments):
        return self.inference_state.execute(self, arguments=arguments)

    def execute_with_values(self, *value_list):
        from jedi.inference.arguments import ValuesArguments
        arguments = ValuesArguments([ValueSet([value]) for value in value_list])
        return self.inference_state.execute(self, arguments)

    def execute_annotation(self):
        return self.execute_with_values()

    def gather_annotation_classes(self):
        return ValueSet([self])

    def merge_types_of_iterate(self, contextualized_node=None, is_async=False):
        return ValueSet.from_sets(
            lazy_value.infer()
            for lazy_value in self.iterate(contextualized_node, is_async)
        )

    def _get_value_filters(self, name_or_str):
        origin_scope = name_or_str if isinstance(name_or_str, Name) else None
        yield from self.get_filters(origin_scope=origin_scope)
        # This covers the case where a stub files are incomplete.
        if self.is_stub():
            from jedi.inference.gradual.conversion import convert_values
            for c in convert_values(ValueSet({self})):
                yield from c.get_filters()

    def goto(self, name_or_str, name_context=None, analysis_errors=True):
        from jedi.inference import finder
        filters = self._get_value_filters(name_or_str)
        names = finder.filter_name(filters, name_or_str)
        debug.dbg('context.goto %s in (%s): %s', name_or_str, self, names)
        return names

    def py__getattribute__(self, name_or_str, name_context=None, position=None,
                           analysis_errors=True):
        """
        :param position: Position of the last statement -> tuple of line, column
        """
        if name_context is None:
            name_context = self
        names = self.goto(name_or_str, name_context, analysis_errors)
```
