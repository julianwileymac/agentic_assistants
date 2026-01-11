# Chunk: a7ecdae35fa6_0

- source: `.venv-lab/Lib/site-packages/jedi/inference/flow_analysis.py`
- lines: 1-81
- chunk: 1/2

```
from typing import Dict, Optional

from jedi.parser_utils import get_flow_branch_keyword, is_scope, get_parent_scope
from jedi.inference.recursion import execution_allowed
from jedi.inference.helpers import is_big_annoying_library


class Status:
    lookup_table: Dict[Optional[bool], 'Status'] = {}

    def __init__(self, value: Optional[bool], name: str) -> None:
        self._value = value
        self._name = name
        Status.lookup_table[value] = self

    def invert(self):
        if self is REACHABLE:
            return UNREACHABLE
        elif self is UNREACHABLE:
            return REACHABLE
        else:
            return UNSURE

    def __and__(self, other):
        if UNSURE in (self, other):
            return UNSURE
        else:
            return REACHABLE if self._value and other._value else UNREACHABLE

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self._name)


REACHABLE = Status(True, 'reachable')
UNREACHABLE = Status(False, 'unreachable')
UNSURE = Status(None, 'unsure')


def _get_flow_scopes(node):
    while True:
        node = get_parent_scope(node, include_flows=True)
        if node is None or is_scope(node):
            return
        yield node


def reachability_check(context, value_scope, node, origin_scope=None):
    if is_big_annoying_library(context) \
            or not context.inference_state.flow_analysis_enabled:
        return UNSURE

    first_flow_scope = get_parent_scope(node, include_flows=True)
    if origin_scope is not None:
        origin_flow_scopes = list(_get_flow_scopes(origin_scope))
        node_flow_scopes = list(_get_flow_scopes(node))

        branch_matches = True
        for flow_scope in origin_flow_scopes:
            if flow_scope in node_flow_scopes:
                node_keyword = get_flow_branch_keyword(flow_scope, node)
                origin_keyword = get_flow_branch_keyword(flow_scope, origin_scope)
                branch_matches = node_keyword == origin_keyword
                if flow_scope.type == 'if_stmt':
                    if not branch_matches:
                        return UNREACHABLE
                elif flow_scope.type == 'try_stmt':
                    if not branch_matches and origin_keyword == 'else' \
                            and node_keyword == 'except':
                        return UNREACHABLE
                if branch_matches:
                    break

        # Direct parents get resolved, we filter scopes that are separate
        # branches.  This makes sense for autocompletion and static analysis.
        # For actual Python it doesn't matter, because we're talking about
        # potentially unreachable code.
        # e.g. `if 0:` would cause all name lookup within the flow make
        # unaccessible. This is not a "problem" in Python, because the code is
        # never called. In Jedi though, we still want to infer types.
        while origin_scope is not None:
```
