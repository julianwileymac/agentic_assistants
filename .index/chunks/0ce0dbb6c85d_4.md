# Chunk: 0ce0dbb6c85d_4

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 303-382
- chunk: 5/9

```
0, yz_node)]``.

        When searching for b in the case ``a, *b, c = [...]`` it will return::

            [(slice(1, -1), abc_node)]
        """
        indexes = []
        is_star_expr = False
        node = self.tree_name.parent
        compare = self.tree_name
        while node is not None:
            if node.type in ('testlist', 'testlist_comp', 'testlist_star_expr', 'exprlist'):
                for i, child in enumerate(node.children):
                    if child == compare:
                        index = int(i / 2)
                        if is_star_expr:
                            from_end = int((len(node.children) - i) / 2)
                            index = slice(index, -from_end)
                        indexes.insert(0, (index, node))
                        break
                else:
                    raise LookupError("Couldn't find the assignment.")
                is_star_expr = False
            elif node.type == 'star_expr':
                is_star_expr = True
            elif node.type in ('expr_stmt', 'sync_comp_for'):
                break

            compare = node
            node = node.parent
        return indexes

    @property
    def inference_state(self):
        # Used by the cache function below
        return self.parent_context.inference_state

    @inference_state_method_cache(default='')
    def py__doc__(self):
        api_type = self.api_type
        if api_type in ('function', 'class', 'property'):
            if self.parent_context.get_root_context().is_stub():
                from jedi.inference.gradual.conversion import convert_names
                names = convert_names([self], prefer_stub_to_compiled=False)
                if self not in names:
                    return _merge_name_docs(names)

            # Make sure the names are not TreeNameDefinitions anymore.
            return clean_scope_docstring(self.tree_name.get_definition())

        if api_type == 'module':
            names = self.goto()
            if self not in names:
                return _merge_name_docs(names)

        if api_type == 'statement' and self.tree_name.is_definition():
            return find_statement_documentation(self.tree_name.get_definition())
        return ''


class _ParamMixin:
    def maybe_positional_argument(self, include_star=True):
        options = [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
        if include_star:
            options.append(Parameter.VAR_POSITIONAL)
        return self.get_kind() in options

    def maybe_keyword_argument(self, include_stars=True):
        options = [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
        if include_stars:
            options.append(Parameter.VAR_KEYWORD)
        return self.get_kind() in options

    def _kind_string(self):
        kind = self.get_kind()
        if kind == Parameter.VAR_POSITIONAL:  # *args
            return '*'
        if kind == Parameter.VAR_KEYWORD:  # **kwargs
            return '**'
```
