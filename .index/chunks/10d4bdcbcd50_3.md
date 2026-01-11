# Chunk: 10d4bdcbcd50_3

- source: `.venv-lab/Lib/site-packages/jedi/plugins/pytest.py`
- lines: 214-270
- chunk: 4/4

```
rt_module(names):
                        yield module_value.as_context()


class FixtureFilter(ParserTreeFilter):
    def _filter(self, names):
        for name in super()._filter(names):
            # look for fixture definitions of imported names
            if name.parent.type == "import_from":
                imported_names = goto_import(self.parent_context, name)
                if any(
                    self._is_fixture(iname.parent_context, iname.tree_name)
                    for iname in imported_names
                    # discard imports of whole modules, that have no tree_name
                    if iname.tree_name
                ):
                    yield name

            elif self._is_fixture(self.parent_context, name):
                yield name

    def _is_fixture(self, context, name):
        funcdef = name.parent
        # Class fixtures are not supported
        if funcdef.type != "funcdef":
            return False
        decorated = funcdef.parent
        if decorated.type != "decorated":
            return False
        decorators = decorated.children[0]
        if decorators.type == 'decorators':
            decorators = decorators.children
        else:
            decorators = [decorators]
        for decorator in decorators:
            dotted_name = decorator.children[1]
            # A heuristic, this makes it faster.
            if 'fixture' in dotted_name.get_code():
                if dotted_name.type == 'atom_expr':
                    # Since Python3.9 a decorator does not have dotted names
                    # anymore.
                    last_trailer = dotted_name.children[-1]
                    last_leaf = last_trailer.get_last_leaf()
                    if last_leaf == ')':
                        values = infer_call_of_leaf(
                            context, last_leaf, cut_own_trailer=True
                        )
                    else:
                        values = context.infer_node(dotted_name)
                else:
                    values = context.infer_node(dotted_name)
                for value in values:
                    if value.name.get_qualified_names(include_module_names=True) \
                            == ('_pytest', 'fixtures', 'fixture'):
                        return True
        return False
```
