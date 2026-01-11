# Chunk: f6cd2cb7ea21_3

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 223-293
- chunk: 4/7

```
nt_path == self._path \
                                or self._path not in parent_path.parents:
                            break
                        if not add_init_paths \
                                and parent_path.joinpath("__init__.py").is_file():
                            continue
                        traversed.append(str(parent_path))

                    # AFAIK some libraries have imports like `foo.foo.bar`, which
                    # leads to the conclusion to by default prefer longer paths
                    # rather than shorter ones by default.
                    suffixed += reversed(traversed)

        if self._django:
            prefixed.append(str(self._path))

        path = prefixed + sys_path + suffixed
        return list(_remove_duplicates_from_path(path))

    def get_environment(self):
        if self._environment is None:
            if self._environment_path is not None:
                self._environment = create_environment(self._environment_path, safe=False)
            else:
                self._environment = get_cached_default_environment()
        return self._environment

    def search(self, string, *, all_scopes=False):
        """
        Searches a name in the whole project. If the project is very big,
        at some point Jedi will stop searching. However it's also very much
        recommended to not exhaust the generator. Just display the first ten
        results to the user.

        There are currently three different search patterns:

        - ``foo`` to search for a definition foo in any file or a file called
          ``foo.py`` or ``foo.pyi``.
        - ``foo.bar`` to search for the ``foo`` and then an attribute ``bar``
          in it.
        - ``class foo.bar.Bar`` or ``def foo.bar.baz`` to search for a specific
          API type.

        :param bool all_scopes: Default False; searches not only for
            definitions on the top level of a module level, but also in
            functions and classes.
        :yields: :class:`.Name`
        """
        return self._search_func(string, all_scopes=all_scopes)

    def complete_search(self, string, **kwargs):
        """
        Like :meth:`.Script.search`, but completes that string. An empty string
        lists all definitions in a project, so be careful with that.

        :param bool all_scopes: Default False; searches not only for
            definitions on the top level of a module level, but also in
            functions and classes.
        :yields: :class:`.Completion`
        """
        return self._search_func(string, complete=True, **kwargs)

    @_try_to_skip_duplicates
    def _search_func(self, string, complete=False, all_scopes=False):
        # Using a Script is they easiest way to get an empty module context.
        from jedi import Script
        s = Script('', project=self)
        inference_state = s._inference_state
        empty_module_context = s._get_module_context()
```
