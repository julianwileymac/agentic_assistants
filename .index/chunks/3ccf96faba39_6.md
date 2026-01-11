# Chunk: 3ccf96faba39_6

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 383-458
- chunk: 7/11

```
tion)
        debug.dbg('global completion scope: %s', context)
        flow_scope_node = get_flow_scope_node(self._module_node, self._position)
        filters = get_global_filters(
            context,
            self._position,
            flow_scope_node
        )
        completion_names = []
        for filter in filters:
            completion_names += filter.values()
        return completion_names

    def _complete_trailer(self, previous_leaf):
        inferred_context = self._module_context.create_context(previous_leaf)
        values = infer_call_of_leaf(inferred_context, previous_leaf)
        debug.dbg('trailer completion values: %s', values, color='MAGENTA')

        # The cached name simply exists to make speed optimizations for certain
        # modules.
        cached_name = None
        if len(values) == 1:
            v, = values
            if v.is_module():
                if len(v.string_names) == 1:
                    module_name = v.string_names[0]
                    if module_name in ('numpy', 'tensorflow', 'matplotlib', 'pandas'):
                        cached_name = module_name

        return cached_name, self._complete_trailer_for_values(values)

    def _complete_trailer_for_values(self, values):
        user_context = get_user_context(self._module_context, self._position)

        return complete_trailer(user_context, values)

    def _get_importer_names(self, names, level=0, only_modules=True):
        names = [n.value for n in names]
        i = imports.Importer(self._inference_state, names, self._module_context, level)
        return i.completion_names(self._inference_state, only_modules=only_modules)

    def _complete_inherited(self, is_function=True):
        """
        Autocomplete inherited methods when overriding in child class.
        """
        leaf = self._module_node.get_leaf_for_position(self._position, include_prefixes=True)
        cls = tree.search_ancestor(leaf, 'classdef')
        if cls is None:
            return

        # Complete the methods that are defined in the super classes.
        class_value = self._module_context.create_value(cls)

        if cls.start_pos[1] >= leaf.start_pos[1]:
            return

        filters = class_value.get_filters(is_instance=True)
        # The first dict is the dictionary of class itself.
        next(filters)
        for filter in filters:
            for name in filter.values():
                # TODO we should probably check here for properties
                if (name.api_type == 'function') == is_function:
                    yield name

    def _complete_in_string(self, start_leaf, string):
        """
        To make it possible for people to have completions in doctests or
        generally in "Python" code in docstrings, we use the following
        heuristic:

        - Having an indented block of code
        - Having some doctest code that starts with `>>>`
        - Having backticks that doesn't have whitespace inside it
        """
```
