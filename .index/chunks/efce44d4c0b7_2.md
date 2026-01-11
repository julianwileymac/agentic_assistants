# Chunk: efce44d4c0b7_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/star_args.py`
- lines: 152-221
- chunk: 3/3

```
_count = 1

        for signature in func.get_signatures():
            found_arg_signature = True
            if new_star_count == 3:
                found_kwarg_signature = True
            args_for_this_func = []
            for p in process_params(
                    list(_remove_given_params(
                        arguments,
                        signature.get_param_names(resolve_stars=False)
                    )), new_star_count):
                if p.get_kind() == Parameter.VAR_KEYWORD:
                    kwarg_names.append(p)
                elif p.get_kind() == Parameter.VAR_POSITIONAL:
                    arg_names.append(p)
                elif p.get_kind() == Parameter.KEYWORD_ONLY:
                    kw_only_names.append(p)
                else:
                    args_for_this_func.append(p)
            if len(args_for_this_func) > len(longest_param_names):
                longest_param_names = args_for_this_func

    for p in longest_param_names:
        if star_count == 1 and p.get_kind() != Parameter.VAR_POSITIONAL:
            yield ParamNameFixedKind(p, Parameter.POSITIONAL_ONLY)
        else:
            if p.get_kind() == Parameter.POSITIONAL_OR_KEYWORD:
                used_names.add(p.string_name)
            yield p

    if not found_arg_signature and original_arg_name is not None:
        yield original_arg_name
    elif arg_names:
        yield arg_names[0]

    # Then process **kwargs
    for func, arguments in kwarg_callables:
        for signature in func.get_signatures():
            found_kwarg_signature = True
            for p in process_params(
                    list(_remove_given_params(
                        arguments,
                        signature.get_param_names(resolve_stars=False)
                    )), star_count=2):
                if p.get_kind() == Parameter.VAR_KEYWORD:
                    kwarg_names.append(p)
                elif p.get_kind() == Parameter.KEYWORD_ONLY:
                    kw_only_names.append(p)

    for p in kw_only_names:
        if p.string_name in used_names:
            continue
        yield p
        used_names.add(p.string_name)

    if not found_kwarg_signature and original_kwarg_name is not None:
        yield original_kwarg_name
    elif kwarg_names:
        yield kwarg_names[0]


class ParamNameFixedKind(ParamNameWrapper):
    def __init__(self, param_name, new_kind):
        super().__init__(param_name)
        self._new_kind = new_kind

    def get_kind(self):
        return self._new_kind
```
