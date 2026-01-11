# Chunk: 3ccf96faba39_8

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 523-598
- chunk: 9/11

```
tion)[match.end():], leaf, start

    if position < leaf.start_pos:
        return None, None, None

    if leaf.type == 'string':
        return return_part_of_leaf(leaf)

    leaves = []
    while leaf is not None:
        if leaf.type == 'error_leaf' and ('"' in leaf.value or "'" in leaf.value):
            if len(leaf.value) > 1:
                return return_part_of_leaf(leaf)
            prefix_leaf = None
            if not leaf.prefix:
                prefix_leaf = leaf.get_previous_leaf()
                if prefix_leaf is None or prefix_leaf.type != 'name' \
                        or not all(c in 'rubf' for c in prefix_leaf.value.lower()):
                    prefix_leaf = None

            return (
                ''.join(cut_value_at_position(l, position) for l in leaves),
                prefix_leaf or leaf,
                ('' if prefix_leaf is None else prefix_leaf.value)
                + cut_value_at_position(leaf, position),
            )
        if leaf.line != position[0]:
            # Multi line strings are always simple error leaves and contain the
            # whole string, single line error leaves are atherefore important
            # now and since the line is different, it's not really a single
            # line string anymore.
            break
        leaves.insert(0, leaf)
        leaf = leaf.get_previous_leaf()
    return None, None, None


def complete_trailer(user_context, values):
    completion_names = []
    for value in values:
        for filter in value.get_filters(origin_scope=user_context.tree_node):
            completion_names += filter.values()

        if not value.is_stub() and isinstance(value, TreeInstance):
            completion_names += _complete_getattr(user_context, value)

    python_values = convert_values(values)
    for c in python_values:
        if c not in values:
            for filter in c.get_filters(origin_scope=user_context.tree_node):
                completion_names += filter.values()
    return completion_names


def _complete_getattr(user_context, instance):
    """
    A heuristic to make completion for proxy objects work. This is not
    intended to work in all cases. It works exactly in this case:

        def __getattr__(self, name):
            ...
            return getattr(any_object, name)

    It is important that the return contains getattr directly, otherwise it
    won't work anymore. It's really just a stupid heuristic. It will not
    work if you write e.g. `return (getatr(o, name))`, because of the
    additional parentheses. It will also not work if you move the getattr
    to some other place that is not the return statement itself.

    It is intentional that it doesn't work in all cases. Generally it's
    really hard to do even this case (as you can see below). Most people
    will write it like this anyway and the other ones, well they are just
    out of luck I guess :) ~dave.
    """
    names = (instance.get_function_slot_names('__getattr__')
```
