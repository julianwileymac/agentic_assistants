# Chunk: f6cd2cb7ea21_4

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 286-355
- chunk: 5/7

```
unc(self, string, complete=False, all_scopes=False):
        # Using a Script is they easiest way to get an empty module context.
        from jedi import Script
        s = Script('', project=self)
        inference_state = s._inference_state
        empty_module_context = s._get_module_context()

        debug.dbg('Search for string %s, complete=%s', string, complete)
        wanted_type, wanted_names = split_search_string(string)
        name = wanted_names[0]
        stub_folder_name = name + '-stubs'

        ios = recurse_find_python_folders_and_files(FolderIO(str(self._path)))
        file_ios = []

        # 1. Search for modules in the current project
        for folder_io, file_io in ios:
            if file_io is None:
                file_name = folder_io.get_base_name()
                if file_name == name or file_name == stub_folder_name:
                    f = folder_io.get_file_io('__init__.py')
                    try:
                        m = load_module_from_path(inference_state, f).as_context()
                    except FileNotFoundError:
                        f = folder_io.get_file_io('__init__.pyi')
                        try:
                            m = load_module_from_path(inference_state, f).as_context()
                        except FileNotFoundError:
                            m = load_namespace_from_path(inference_state, folder_io).as_context()
                else:
                    continue
            else:
                file_ios.append(file_io)
                if Path(file_io.path).name in (name + '.py', name + '.pyi'):
                    m = load_module_from_path(inference_state, file_io).as_context()
                else:
                    continue

            debug.dbg('Search of a specific module %s', m)
            yield from search_in_module(
                inference_state,
                m,
                names=[m.name],
                wanted_type=wanted_type,
                wanted_names=wanted_names,
                complete=complete,
                convert=True,
                ignore_imports=True,
            )

        # 2. Search for identifiers in the project.
        for module_context in search_in_file_ios(inference_state, file_ios,
                                                 name, complete=complete):
            names = get_module_names(module_context.tree_node, all_scopes=all_scopes)
            names = [module_context.create_name(n) for n in names]
            names = _remove_imports(names)
            yield from search_in_module(
                inference_state,
                module_context,
                names=names,
                wanted_type=wanted_type,
                wanted_names=wanted_names,
                complete=complete,
                ignore_imports=True,
            )

        # 3. Search for modules on sys.path
        sys_path = [
            p for p in self._get_sys_path(inference_state)
```
