# Chunk: 10d4bdcbcd50_1

- source: `.venv-lab/Lib/site-packages/jedi/plugins/pytest.py`
- lines: 73-159
- chunk: 2/4

```
ures
                    for value in fixture.infer()
                )
        return func(param_name)
    return wrapper


def goto_anonymous_param(func):
    def wrapper(param_name):
        is_pytest_param, param_name_is_function_name = \
            _is_a_pytest_param_and_inherited(param_name)
        if is_pytest_param:
            names = _goto_pytest_fixture(
                param_name.get_root_context(),
                param_name.string_name,
                skip_own_module=param_name_is_function_name,
            )
            if names:
                return names
        return func(param_name)
    return wrapper


def complete_param_names(func):
    def wrapper(context, func_name, decorator_nodes):
        module_context = context.get_root_context()
        if _is_pytest_func(func_name, decorator_nodes):
            names = []
            for module_context in _iter_pytest_modules(module_context):
                names += FixtureFilter(module_context).values()
            if names:
                return names
        return func(context, func_name, decorator_nodes)
    return wrapper


def _goto_pytest_fixture(module_context, name, skip_own_module):
    for module_context in _iter_pytest_modules(module_context, skip_own_module=skip_own_module):
        names = FixtureFilter(module_context).get(name)
        if names:
            return names


def _is_a_pytest_param_and_inherited(param_name):
    """
    Pytest params are either in a `test_*` function or have a pytest fixture
    with the decorator @pytest.fixture.

    This is a heuristic and will work in most cases.
    """
    funcdef = search_ancestor(param_name.tree_name, 'funcdef')
    if funcdef is None:  # A lambda
        return False, False
    decorators = funcdef.get_decorators()
    return _is_pytest_func(funcdef.name.value, decorators), \
        funcdef.name.value == param_name.string_name


def _is_pytest_func(func_name, decorator_nodes):
    return func_name.startswith('test') \
        or any('fixture' in n.get_code() for n in decorator_nodes)


def _find_pytest_plugin_modules() -> List[List[str]]:
    """
    Finds pytest plugin modules hooked by setuptools entry points

    See https://docs.pytest.org/en/stable/how-to/writing_plugins.html#setuptools-entry-points
    """
    if sys.version_info >= (3, 8):
        from importlib.metadata import entry_points

        if sys.version_info >= (3, 10):
            pytest_entry_points = entry_points(group="pytest11")
        else:
            pytest_entry_points = entry_points().get("pytest11", ())

        if sys.version_info >= (3, 9):
            return [ep.module.split(".") for ep in pytest_entry_points]
        else:
            # Python 3.8 doesn't have `EntryPoint.module`. Implement equivalent
            # to what Python 3.9 does (with additional None check to placate `mypy`)
            matches = [
                ep.pattern.match(ep.value)
                for ep in pytest_entry_points
            ]
```
