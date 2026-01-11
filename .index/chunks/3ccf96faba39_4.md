# Chunk: 3ccf96faba39_4

- source: `.venv-lab/Lib/site-packages/jedi/api/completion.py`
- lines: 277-331
- chunk: 5/11

```
)
            if nodes and nodes[-1] in ('as', 'def', 'class'):
                # No completions for ``with x as foo`` and ``import x as foo``.
                # Also true for defining names as a class or function.
                return cached_name, list(self._complete_inherited(is_function=True))
            elif "import_stmt" in nonterminals:
                level, names = parse_dotted_names(nodes, "import_from" in nonterminals)

                only_modules = not ("import_from" in nonterminals and 'import' in nodes)
                completion_names += self._get_importer_names(
                    names,
                    level,
                    only_modules=only_modules,
                )
            elif nonterminals[-1] in ('trailer', 'dotted_name') and nodes[-1] == '.':
                dot = self._module_node.get_leaf_for_position(self._position)
                if dot.type == "endmarker":
                    # This is a bit of a weird edge case, maybe we can somehow
                    # generalize this.
                    dot = leaf.get_previous_leaf()
                cached_name, n = self._complete_trailer(dot.get_previous_leaf())
                completion_names += n
            elif self._is_parameter_completion():
                completion_names += self._complete_params(leaf)
            else:
                # Apparently this looks like it's good enough to filter most cases
                # so that signature completions don't randomly appear.
                # To understand why this works, three things are important:
                # 1. trailer with a `,` in it is either a subscript or an arglist.
                # 2. If there's no `,`, it's at the start and only signatures start
                #    with `(`. Other trailers could start with `.` or `[`.
                # 3. Decorators are very primitive and have an optional `(` with
                #    optional arglist in them.
                if nodes[-1] in ['(', ','] \
                        and nonterminals[-1] in ('trailer', 'arglist', 'decorator'):
                    signatures = self._signatures_callback(*self._position)
                    if signatures:
                        call_details = signatures[0]._call_details
                        used_kwargs = list(call_details.iter_used_keyword_arguments())
                        positional_count = call_details.count_positional_arguments()

                        completion_names += _get_signature_param_names(
                            signatures,
                            positional_count,
                            used_kwargs,
                        )

                        kwargs_only = _must_be_kwarg(signatures, positional_count, used_kwargs)

                if not kwargs_only:
                    completion_names += self._complete_global_scope()
                    completion_names += self._complete_inherited(is_function=False)

        if not kwargs_only:
```
