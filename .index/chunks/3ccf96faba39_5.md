# Chunk: 3ccf96faba39_5

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 324-392
- chunk: 6/11

```
        kwargs_only = _must_be_kwarg(signatures, positional_count, used_kwargs)

                if not kwargs_only:
                    completion_names += self._complete_global_scope()
                    completion_names += self._complete_inherited(is_function=False)

        if not kwargs_only:
            current_line = self._code_lines[self._position[0] - 1][:self._position[1]]
            completion_names += self._complete_keywords(
                allowed_transitions,
                only_values=not (not current_line or current_line[-1] in ' \t.;'
                                 and current_line[-3:] != '...')
            )

        return cached_name, completion_names

    def _is_parameter_completion(self):
        tos = self.stack[-1]
        if tos.nonterminal == 'lambdef' and len(tos.nodes) == 1:
            # We are at the position `lambda `, where basically the next node
            # is a param.
            return True
        if tos.nonterminal in 'parameters':
            # Basically we are at the position `foo(`, there's nothing there
            # yet, so we have no `typedargslist`.
            return True
        # var args is for lambdas and typed args for normal functions
        return tos.nonterminal in ('typedargslist', 'varargslist') and tos.nodes[-1] == ','

    def _complete_params(self, leaf):
        stack_node = self.stack[-2]
        if stack_node.nonterminal == 'parameters':
            stack_node = self.stack[-3]
        if stack_node.nonterminal == 'funcdef':
            context = get_user_context(self._module_context, self._position)
            node = search_ancestor(leaf, 'error_node', 'funcdef')
            if node is not None:
                if node.type == 'error_node':
                    n = node.children[0]
                    if n.type == 'decorators':
                        decorators = n.children
                    elif n.type == 'decorator':
                        decorators = [n]
                    else:
                        decorators = []
                else:
                    decorators = node.get_decorators()
                function_name = stack_node.nodes[1]

                return complete_param_names(context, function_name.value, decorators)
        return []

    def _complete_keywords(self, allowed_transitions, only_values):
        for k in allowed_transitions:
            if isinstance(k, str) and k.isalpha():
                if not only_values or k in ('True', 'False', 'None'):
                    yield keywords.KeywordName(self._inference_state, k)

    def _complete_global_scope(self):
        context = get_user_context(self._module_context, self._position)
        debug.dbg('global completion scope: %s', context)
        flow_scope_node = get_flow_scope_node(self._module_node, self._position)
        filters = get_global_filters(
            context,
            self._position,
            flow_scope_node
        )
        completion_names = []
```
