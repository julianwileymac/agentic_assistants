# Chunk: 3ccf96faba39_9

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 592-663
- chunk: 10/11

```
that it doesn't work in all cases. Generally it's
    really hard to do even this case (as you can see below). Most people
    will write it like this anyway and the other ones, well they are just
    out of luck I guess :) ~dave.
    """
    names = (instance.get_function_slot_names('__getattr__')
             or instance.get_function_slot_names('__getattribute__'))
    functions = ValueSet.from_sets(
        name.infer()
        for name in names
    )
    for func in functions:
        tree_node = func.tree_node
        if tree_node is None or tree_node.type != 'funcdef':
            continue

        for return_stmt in tree_node.iter_return_stmts():
            # Basically until the next comment we just try to find out if a
            # return statement looks exactly like `return getattr(x, name)`.
            if return_stmt.type != 'return_stmt':
                continue
            atom_expr = return_stmt.children[1]
            if atom_expr.type != 'atom_expr':
                continue
            atom = atom_expr.children[0]
            trailer = atom_expr.children[1]
            if len(atom_expr.children) != 2 or atom.type != 'name' \
                    or atom.value != 'getattr':
                continue
            arglist = trailer.children[1]
            if arglist.type != 'arglist' or len(arglist.children) < 3:
                continue
            context = func.as_context()
            object_node = arglist.children[0]

            # Make sure it's a param: foo in __getattr__(self, foo)
            name_node = arglist.children[2]
            name_list = context.goto(name_node, name_node.start_pos)
            if not any(n.api_type == 'param' for n in name_list):
                continue

            # Now that we know that these are most probably completion
            # objects, we just infer the object and return them as
            # completions.
            objects = context.infer_node(object_node)
            return complete_trailer(user_context, objects)
    return []


def search_in_module(inference_state, module_context, names, wanted_names,
                     wanted_type, complete=False, fuzzy=False,
                     ignore_imports=False, convert=False):
    for s in wanted_names[:-1]:
        new_names = []
        for n in names:
            if s == n.string_name:
                if n.tree_name is not None and n.api_type in ('module', 'namespace') \
                        and ignore_imports:
                    continue
                new_names += complete_trailer(
                    module_context,
                    n.infer()
                )
        debug.dbg('dot lookup on search %s from %s', new_names, names[:10])
        names = new_names

    last_name = wanted_names[-1].lower()
    for n in names:
        string = n.string_name.lower()
        if complete and helpers.match(string, last_name, fuzzy=fuzzy) \
                or not complete and string == last_name:
```
