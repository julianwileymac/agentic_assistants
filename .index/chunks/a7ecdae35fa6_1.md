# Chunk: a7ecdae35fa6_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/flow_analysis.py`
- lines: 76-126
- chunk: 2/2

```
       # potentially unreachable code.
        # e.g. `if 0:` would cause all name lookup within the flow make
        # unaccessible. This is not a "problem" in Python, because the code is
        # never called. In Jedi though, we still want to infer types.
        while origin_scope is not None:
            if first_flow_scope == origin_scope and branch_matches:
                return REACHABLE
            origin_scope = origin_scope.parent

    return _break_check(context, value_scope, first_flow_scope, node)


def _break_check(context, value_scope, flow_scope, node):
    reachable = REACHABLE
    if flow_scope.type == 'if_stmt':
        if flow_scope.is_node_after_else(node):
            for check_node in flow_scope.get_test_nodes():
                reachable = _check_if(context, check_node)
                if reachable in (REACHABLE, UNSURE):
                    break
            reachable = reachable.invert()
        else:
            flow_node = flow_scope.get_corresponding_test_node(node)
            if flow_node is not None:
                reachable = _check_if(context, flow_node)
    elif flow_scope.type in ('try_stmt', 'while_stmt'):
        return UNSURE

    # Only reachable branches need to be examined further.
    if reachable in (UNREACHABLE, UNSURE):
        return reachable

    if value_scope != flow_scope and value_scope != flow_scope.parent:
        flow_scope = get_parent_scope(flow_scope, include_flows=True)
        return reachable & _break_check(context, value_scope, flow_scope, node)
    else:
        return reachable


def _check_if(context, node):
    with execution_allowed(context.inference_state, node) as allowed:
        if not allowed:
            return UNSURE

        types = context.infer_node(node)
        values = set(x.py__bool__() for x in types)
        if len(values) == 1:
            return Status.lookup_table[values.pop()]
        else:
            return UNSURE
```
