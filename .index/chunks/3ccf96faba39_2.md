# Chunk: 3ccf96faba39_2

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 150-221
- chunk: 3/11

```
osition(
            self._original_position,
            include_prefixes=True
        )
        string, start_leaf, quote = _extract_string_while_in_string(leaf, self._original_position)

        prefixed_completions = complete_dict(
            self._module_context,
            self._code_lines,
            start_leaf or leaf,
            self._original_position,
            None if string is None else quote + string,
            fuzzy=self._fuzzy,
        )

        if string is not None and not prefixed_completions:
            prefixed_completions = list(complete_file_name(
                self._inference_state, self._module_context, start_leaf, quote, string,
                self._like_name, self._signatures_callback,
                self._code_lines, self._original_position,
                self._fuzzy
            ))
        if string is not None:
            if not prefixed_completions and '\n' in string:
                # Complete only multi line strings
                prefixed_completions = self._complete_in_string(start_leaf, string)
            return prefixed_completions

        cached_name, completion_names = self._complete_python(leaf)

        imported_names = []
        if leaf.parent is not None and leaf.parent.type in ['import_as_names', 'dotted_as_names']:
            imported_names.extend(extract_imported_names(leaf.parent))

        completions = list(filter_names(self._inference_state, completion_names,
                                        self.stack, self._like_name,
                                        self._fuzzy, imported_names, cached_name=cached_name))

        return (
            # Removing duplicates mostly to remove False/True/None duplicates.
            _remove_duplicates(prefixed_completions, completions)
            + sorted(completions, key=lambda x: (not x.name.startswith(self._like_name),
                                                 x.name.startswith('__'),
                                                 x.name.startswith('_'),
                                                 x.name.lower()))
        )

    def _complete_python(self, leaf):
        """
        Analyzes the current context of a completion and decides what to
        return.

        Technically this works by generating a parser stack and analysing the
        current stack for possible grammar nodes.

        Possible enhancements:
        - global/nonlocal search global
        - yield from / raise from <- could be only exceptions/generators
        - In args: */**: no completion
        - In params (also lambda): no completion before =
        """
        grammar = self._inference_state.grammar
        self.stack = stack = None
        self._position = (
            self._original_position[0],
            self._original_position[1] - len(self._like_name)
        )
        cached_name = None

        try:
            self.stack = stack = helpers.get_stack_at_position(
```
