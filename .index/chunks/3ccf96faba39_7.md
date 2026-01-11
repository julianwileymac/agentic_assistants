# Chunk: 3ccf96faba39_7

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 450-534
- chunk: 8/11

```
ve completions in doctests or
        generally in "Python" code in docstrings, we use the following
        heuristic:

        - Having an indented block of code
        - Having some doctest code that starts with `>>>`
        - Having backticks that doesn't have whitespace inside it
        """

        def iter_relevant_lines(lines):
            include_next_line = False
            for l in code_lines:
                if include_next_line or l.startswith('>>>') or l.startswith(' '):
                    yield re.sub(r'^( *>>> ?| +)', '', l)
                else:
                    yield None

                include_next_line = bool(re.match(' *>>>', l))

        string = dedent(string)
        code_lines = split_lines(string, keepends=True)
        relevant_code_lines = list(iter_relevant_lines(code_lines))
        if relevant_code_lines[-1] is not None:
            # Some code lines might be None, therefore get rid of that.
            relevant_code_lines = ['\n' if c is None else c for c in relevant_code_lines]
            return self._complete_code_lines(relevant_code_lines)
        match = re.search(r'`([^`\s]+)', code_lines[-1])
        if match:
            return self._complete_code_lines([match.group(1)])
        return []

    def _complete_code_lines(self, code_lines):
        module_node = self._inference_state.grammar.parse(''.join(code_lines))
        module_value = DocstringModule(
            in_module_context=self._module_context,
            inference_state=self._inference_state,
            module_node=module_node,
            code_lines=code_lines,
        )
        return Completion(
            self._inference_state,
            module_value.as_context(),
            code_lines=code_lines,
            position=module_node.end_pos,
            signatures_callback=lambda *args, **kwargs: [],
            fuzzy=self._fuzzy
        ).complete()


def _gather_nodes(stack):
    nodes = []
    for stack_node in stack:
        if stack_node.dfa.from_rule == 'small_stmt':
            nodes = []
        else:
            nodes += stack_node.nodes
    return nodes


_string_start = re.compile(r'^\w*(\'{3}|"{3}|\'|")')


def _extract_string_while_in_string(leaf, position):
    def return_part_of_leaf(leaf):
        kwargs = {}
        if leaf.line == position[0]:
            kwargs['endpos'] = position[1] - leaf.column
        match = _string_start.match(leaf.value, **kwargs)
        if not match:
            return None, None, None
        start = match.group(0)
        if leaf.line == position[0] and position[1] < leaf.column + match.end():
            return None, None, None
        return cut_value_at_position(leaf, position)[match.end():], leaf, start

    if position < leaf.start_pos:
        return None, None, None

    if leaf.type == 'string':
        return return_part_of_leaf(leaf)

    leaves = []
    while leaf is not None:
        if leaf.type == 'error_leaf' and ('"' in leaf.value or "'" in leaf.value):
```
