# Chunk: e370edcf8fd5_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/filters.py`
- lines: 150-244
- chunk: 3/5

```
 False
        base_node = parent if parent.type in ('classdef', 'funcdef') else name
        return get_cached_parent_scope(self._parso_cache_node, base_node) == self._parser_scope

    def _check_flows(self, names):
        for name in sorted(names, key=lambda name: name.start_pos, reverse=True):
            check = flow_analysis.reachability_check(
                context=self._node_context,
                value_scope=self._parser_scope,
                node=name,
                origin_scope=self._origin_scope
            )
            if check is not flow_analysis.UNREACHABLE:
                yield name

            if check is flow_analysis.REACHABLE:
                break


class _FunctionExecutionFilter(ParserTreeFilter):
    def __init__(self, parent_context, function_value, until_position, origin_scope):
        super().__init__(
            parent_context,
            until_position=until_position,
            origin_scope=origin_scope,
        )
        self._function_value = function_value

    def _convert_param(self, param, name):
        raise NotImplementedError

    @to_list
    def _convert_names(self, names):
        for name in names:
            param = search_ancestor(name, 'param')
            # Here we don't need to check if the param is a default/annotation,
            # because those are not definitions and never make it to this
            # point.
            if param:
                yield self._convert_param(param, name)
            else:
                yield TreeNameDefinition(self.parent_context, name)


class FunctionExecutionFilter(_FunctionExecutionFilter):
    def __init__(self, *args, arguments, **kwargs):
        super().__init__(*args, **kwargs)
        self._arguments = arguments

    def _convert_param(self, param, name):
        return ParamName(self._function_value, name, self._arguments)


class AnonymousFunctionExecutionFilter(_FunctionExecutionFilter):
    def _convert_param(self, param, name):
        return AnonymousParamName(self._function_value, name)


class GlobalNameFilter(_AbstractUsedNamesFilter):
    def get(self, name):
        try:
            names = self._used_names[name]
        except KeyError:
            return []
        return self._convert_names(self._filter(names))

    @to_list
    def _filter(self, names):
        for name in names:
            if name.parent.type == 'global_stmt':
                yield name

    def values(self):
        return self._convert_names(
            name for name_list in self._used_names.values()
            for name in self._filter(name_list)
        )


class DictFilter(AbstractFilter):
    def __init__(self, dct):
        self._dct = dct

    def get(self, name):
        try:
            value = self._convert(name, self._dct[name])
        except KeyError:
            return []
        else:
            return list(self._filter([value]))

    def values(self):
        def yielder():
            for item in self._dct.items():
```
