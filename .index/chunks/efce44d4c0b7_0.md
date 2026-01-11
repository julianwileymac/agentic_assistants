# Chunk: efce44d4c0b7_0

- source: `.venv-lab/Lib/site-packages/jedi/inference/star_args.py`
- lines: 1-78
- chunk: 1/3

```
"""
This module is responsible for inferring *args and **kwargs for signatures.

This means for example in this case::

    def foo(a, b, c): ...

    def bar(*args):
        return foo(1, *args)

The signature here for bar should be `bar(b, c)` instead of bar(*args).
"""
from inspect import Parameter

from parso import tree

from jedi.inference.utils import to_list
from jedi.inference.names import ParamNameWrapper
from jedi.inference.helpers import is_big_annoying_library


def _iter_nodes_for_param(param_name):
    from parso.python.tree import search_ancestor
    from jedi.inference.arguments import TreeArguments

    execution_context = param_name.parent_context
    # Walk up the parso tree to get the FunctionNode we want. We use the parso
    # tree rather than going via the execution context so that we're agnostic of
    # the specific scope we're evaluating within (i.e: module or function,
    # etc.).
    function_node = tree.search_ancestor(param_name.tree_name, 'funcdef', 'lambdef')
    module_node = function_node.get_root_node()
    start = function_node.children[-1].start_pos
    end = function_node.children[-1].end_pos
    for name in module_node.get_used_names().get(param_name.string_name):
        if start <= name.start_pos < end:
            # Is used in the function
            argument = name.parent
            if argument.type == 'argument' \
                    and argument.children[0] == '*' * param_name.star_count:
                trailer = search_ancestor(argument, 'trailer')
                if trailer is not None:  # Make sure we're in a function
                    context = execution_context.create_context(trailer)
                    if _goes_to_param_name(param_name, context, name):
                        values = _to_callables(context, trailer)

                        args = TreeArguments.create_cached(
                            execution_context.inference_state,
                            context=context,
                            argument_node=trailer.children[1],
                            trailer=trailer,
                        )
                        for c in values:
                            yield c, args


def _goes_to_param_name(param_name, context, potential_name):
    if potential_name.type != 'name':
        return False
    from jedi.inference.names import TreeNameDefinition
    found = TreeNameDefinition(context, potential_name).goto()
    return any(param_name.parent_context == p.parent_context
               and param_name.start_pos == p.start_pos
               for p in found)


def _to_callables(context, trailer):
    from jedi.inference.syntax_tree import infer_trailer

    atom_expr = trailer.parent
    index = atom_expr.children[0] == 'await'
    # Infer atom first
    values = context.infer_node(atom_expr.children[index])
    for trailer2 in atom_expr.children[index + 1:]:
        if trailer == trailer2:
            break
        values = infer_trailer(context, values, trailer2)
```
