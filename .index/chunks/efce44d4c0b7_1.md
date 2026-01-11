# Chunk: efce44d4c0b7_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/star_args.py`
- lines: 70-161
- chunk: 2/3

```
ailer.parent
    index = atom_expr.children[0] == 'await'
    # Infer atom first
    values = context.infer_node(atom_expr.children[index])
    for trailer2 in atom_expr.children[index + 1:]:
        if trailer == trailer2:
            break
        values = infer_trailer(context, values, trailer2)
    return values


def _remove_given_params(arguments, param_names):
    count = 0
    used_keys = set()
    for key, _ in arguments.unpack():
        if key is None:
            count += 1
        else:
            used_keys.add(key)

    for p in param_names:
        if count and p.maybe_positional_argument():
            count -= 1
            continue
        if p.string_name in used_keys and p.maybe_keyword_argument():
            continue
        yield p


@to_list
def process_params(param_names, star_count=3):  # default means both * and **
    if param_names:
        if is_big_annoying_library(param_names[0].parent_context):
            # At first this feature can look innocent, but it does a lot of
            # type inference in some cases, so we just ditch it.
            yield from param_names
            return

    used_names = set()
    arg_callables = []
    kwarg_callables = []

    kw_only_names = []
    kwarg_names = []
    arg_names = []
    original_arg_name = None
    original_kwarg_name = None
    for p in param_names:
        kind = p.get_kind()
        if kind == Parameter.VAR_POSITIONAL:
            if star_count & 1:
                arg_callables = _iter_nodes_for_param(p)
                original_arg_name = p
        elif p.get_kind() == Parameter.VAR_KEYWORD:
            if star_count & 2:
                kwarg_callables = list(_iter_nodes_for_param(p))
                original_kwarg_name = p
        elif kind == Parameter.KEYWORD_ONLY:
            if star_count & 2:
                kw_only_names.append(p)
        elif kind == Parameter.POSITIONAL_ONLY:
            if star_count & 1:
                yield p
        else:
            if star_count == 1:
                yield ParamNameFixedKind(p, Parameter.POSITIONAL_ONLY)
            elif star_count == 2:
                kw_only_names.append(ParamNameFixedKind(p, Parameter.KEYWORD_ONLY))
            else:
                used_names.add(p.string_name)
                yield p

    # First process *args
    longest_param_names = ()
    found_arg_signature = False
    found_kwarg_signature = False
    for func_and_argument in arg_callables:
        func, arguments = func_and_argument
        new_star_count = star_count
        if func_and_argument in kwarg_callables:
            kwarg_callables.remove(func_and_argument)
        else:
            new_star_count = 1

        for signature in func.get_signatures():
            found_arg_signature = True
            if new_star_count == 3:
                found_kwarg_signature = True
            args_for_this_func = []
            for p in process_params(
                    list(_remove_given_params(
```
