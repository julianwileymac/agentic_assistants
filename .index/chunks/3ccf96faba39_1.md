# Chunk: 3ccf96faba39_1

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 75-159
- chunk: 2/11

```
tring != like_name:
            continue
        if settings.case_insensitive_completion:
            string = string.lower()
        if helpers.match(string, like_name, fuzzy=fuzzy):
            new = classes.Completion(
                inference_state,
                name,
                stack,
                len(like_name),
                is_fuzzy=fuzzy,
                cached_name=cached_name,
            )
            k = (new.name, new.complete)  # key
            if k not in comp_dct:
                comp_dct.add(k)
                tree_name = name.tree_name
                if tree_name is not None:
                    definition = tree_name.get_definition()
                    if definition is not None and definition.type == 'del_stmt':
                        continue
                yield new


def _remove_duplicates(completions, other_completions):
    names = {d.name for d in other_completions}
    return [c for c in completions if c.name not in names]


def get_user_context(module_context, position):
    """
    Returns the scope in which the user resides. This includes flows.
    """
    leaf = module_context.tree_node.get_leaf_for_position(position, include_prefixes=True)
    return module_context.create_context(leaf)


def get_flow_scope_node(module_node, position):
    node = module_node.get_leaf_for_position(position, include_prefixes=True)
    while not isinstance(node, (tree.Scope, tree.Flow)):
        node = node.parent

    return node


@plugin_manager.decorate()
def complete_param_names(context, function_name, decorator_nodes):
    # Basically there's no way to do param completion. The plugins are
    # responsible for this.
    return []


class Completion:
    def __init__(self, inference_state, module_context, code_lines, position,
                 signatures_callback, fuzzy=False):
        self._inference_state = inference_state
        self._module_context = module_context
        self._module_node = module_context.tree_node
        self._code_lines = code_lines

        # The first step of completions is to get the name
        self._like_name = helpers.get_on_completion_name(self._module_node, code_lines, position)
        # The actual cursor position is not what we need to calculate
        # everything. We want the start of the name we're on.
        self._original_position = position
        self._signatures_callback = signatures_callback

        self._fuzzy = fuzzy

    # Return list of completions in this order:
    # - Beginning with what user is typing
    # - Public (alphabet)
    # - Private ("_xxx")
    # - Dunder ("__xxx")
    def complete(self):
        leaf = self._module_node.get_leaf_for_position(
            self._original_position,
            include_prefixes=True
        )
        string, start_leaf, quote = _extract_string_while_in_string(leaf, self._original_position)

        prefixed_completions = complete_dict(
            self._module_context,
            self._code_lines,
```
