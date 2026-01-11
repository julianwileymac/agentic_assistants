# Chunk: 0ce0dbb6c85d_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 154-224
- chunk: 3/9

```
         return [self]
            elif type_ in ('import_from', 'import_name'):
                from jedi.inference.imports import goto_import
                module_names = goto_import(context, name)
                return module_names
            else:
                return [self]
        else:
            from jedi.inference.imports import follow_error_node_imports_if_possible
            values = follow_error_node_imports_if_possible(context, name)
            if values is not None:
                return [value.name for value in values]

        par = name.parent
        node_type = par.type
        if node_type == 'argument' and par.children[1] == '=' and par.children[0] == name:
            # Named param goto.
            trailer = par.parent
            if trailer.type == 'arglist':
                trailer = trailer.parent
            if trailer.type != 'classdef':
                if trailer.type == 'decorator':
                    value_set = context.infer_node(trailer.children[1])
                else:
                    i = trailer.parent.children.index(trailer)
                    to_infer = trailer.parent.children[:i]
                    if to_infer[0] == 'await':
                        to_infer.pop(0)
                    value_set = context.infer_node(to_infer[0])
                    from jedi.inference.syntax_tree import infer_trailer
                    for trailer in to_infer[1:]:
                        value_set = infer_trailer(context, value_set, trailer)
                param_names = []
                for value in value_set:
                    for signature in value.get_signatures():
                        for param_name in signature.get_param_names():
                            if param_name.string_name == name.value:
                                param_names.append(param_name)
                return param_names
        elif node_type == 'dotted_name':  # Is a decorator.
            index = par.children.index(name)
            if index > 0:
                new_dotted = deep_ast_copy(par)
                new_dotted.children[index - 1:] = []
                values = context.infer_node(new_dotted)
                return unite(
                    value.goto(name, name_context=context)
                    for value in values
                )

        if node_type == 'trailer' and par.children[0] == '.':
            values = infer_call_of_leaf(context, name, cut_own_trailer=True)
            return values.goto(name, name_context=context)
        else:
            stmt = search_ancestor(
                name, 'expr_stmt', 'lambdef'
            ) or name
            if stmt.type == 'lambdef':
                stmt = name
            return context.goto(name, position=stmt.start_pos)

    def is_import(self):
        imp = search_ancestor(self.tree_name, 'import_from', 'import_name')
        return imp is not None

    @property
    def string_name(self):
        return self.tree_name.value

    @property
```
