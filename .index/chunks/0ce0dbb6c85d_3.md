# Chunk: 0ce0dbb6c85d_3

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 212-314
- chunk: 4/9

```
tmt = name
            return context.goto(name, position=stmt.start_pos)

    def is_import(self):
        imp = search_ancestor(self.tree_name, 'import_from', 'import_name')
        return imp is not None

    @property
    def string_name(self):
        return self.tree_name.value

    @property
    def start_pos(self):
        return self.tree_name.start_pos


class ValueNameMixin:
    def infer(self):
        return ValueSet([self._value])

    def py__doc__(self):
        doc = self._value.py__doc__()
        if not doc and self._value.is_stub():
            from jedi.inference.gradual.conversion import convert_names
            names = convert_names([self], prefer_stub_to_compiled=False)
            if self not in names:
                return _merge_name_docs(names)
        return doc

    def _get_qualified_names(self):
        return self._value.get_qualified_names()

    def get_root_context(self):
        if self.parent_context is None:  # A module
            return self._value.as_context()
        return super().get_root_context()

    def get_defining_qualified_value(self):
        context = self.parent_context
        if context is not None and (context.is_module() or context.is_class()):
            return self.parent_context.get_value()  # Might be None
        return None

    @property
    def api_type(self):
        return self._value.api_type


class ValueName(ValueNameMixin, AbstractTreeName):
    def __init__(self, value, tree_name):
        super().__init__(value.parent_context, tree_name)
        self._value = value

    def goto(self):
        return ValueSet([self._value.name])


class TreeNameDefinition(AbstractTreeName):
    _API_TYPES = dict(
        import_name='module',
        import_from='module',
        funcdef='function',
        param='param',
        classdef='class',
    )

    def infer(self):
        # Refactor this, should probably be here.
        from jedi.inference.syntax_tree import tree_name_to_values
        return tree_name_to_values(
            self.parent_context.inference_state,
            self.parent_context,
            self.tree_name
        )

    @property
    def api_type(self):
        definition = self.tree_name.get_definition(import_name_always=True)
        if definition is None:
            return 'statement'
        return self._API_TYPES.get(definition.type, 'statement')

    def assignment_indexes(self):
        """
        Returns an array of tuple(int, node) of the indexes that are used in
        tuple assignments.

        For example if the name is ``y`` in the following code::

            x, (y, z) = 2, ''

        would result in ``[(1, xyz_node), (0, yz_node)]``.

        When searching for b in the case ``a, *b, c = [...]`` it will return::

            [(slice(1, -1), abc_node)]
        """
        indexes = []
        is_star_expr = False
        node = self.tree_name.parent
        compare = self.tree_name
        while node is not None:
```
