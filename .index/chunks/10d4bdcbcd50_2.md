# Chunk: 10d4bdcbcd50_2

- source: `.venv-lab/Lib/site-packages/jedi/plugins/pytest.py`
- lines: 152-223
- chunk: 3/4

```
  else:
            # Python 3.8 doesn't have `EntryPoint.module`. Implement equivalent
            # to what Python 3.9 does (with additional None check to placate `mypy`)
            matches = [
                ep.pattern.match(ep.value)
                for ep in pytest_entry_points
            ]
            return [x.group('module').split(".") for x in matches if x]

    else:
        from pkg_resources import iter_entry_points
        return [ep.module_name.split(".") for ep in iter_entry_points(group="pytest11")]


@inference_state_method_cache()
def _iter_pytest_modules(module_context, skip_own_module=False):
    if not skip_own_module:
        yield module_context

    file_io = module_context.get_value().file_io
    if file_io is not None:
        folder = file_io.get_parent_folder()
        sys_path = module_context.inference_state.get_sys_path()

        # prevent an infinite loop when reaching the root of the current drive
        last_folder = None

        while any(folder.path.startswith(p) for p in sys_path):
            file_io = folder.get_file_io('conftest.py')
            if Path(file_io.path) != module_context.py__file__():
                try:
                    m = load_module_from_path(module_context.inference_state, file_io)
                    conftest_module = m.as_context()
                    yield conftest_module

                    plugins_list = m.tree_node.get_used_names().get("pytest_plugins")
                    if plugins_list:
                        name = conftest_module.create_name(plugins_list[0])
                        yield from _load_pytest_plugins(module_context, name)
                except FileNotFoundError:
                    pass
            folder = folder.get_parent_folder()

            # prevent an infinite for loop if the same parent folder is return twice
            if last_folder is not None and folder.path == last_folder.path:
                break
            last_folder = folder  # keep track of the last found parent name

    for names in _PYTEST_FIXTURE_MODULES + _find_pytest_plugin_modules():
        for module_value in module_context.inference_state.import_module(names):
            yield module_value.as_context()


def _load_pytest_plugins(module_context, name):
    from jedi.inference.helpers import get_str_or_none

    for inferred in name.infer():
        for seq_value in inferred.py__iter__():
            for value in seq_value.infer():
                fq_name = get_str_or_none(value)
                if fq_name:
                    names = fq_name.split(".")
                    for module_value in module_context.inference_state.import_module(names):
                        yield module_value.as_context()


class FixtureFilter(ParserTreeFilter):
    def _filter(self, names):
        for name in super()._filter(names):
            # look for fixture definitions of imported names
            if name.parent.type == "import_from":
```
