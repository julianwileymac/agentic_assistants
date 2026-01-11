# Chunk: 0ce0dbb6c85d_7

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 539-637
- chunk: 8/9

```
 return NO_VALUES
        else:
            return self.function_value.parent_context.infer_node(param.default)
        return ValueSet({value})


class ParamName(_ActualTreeParamName):
    def __init__(self, function_value, tree_name, arguments):
        super().__init__(function_value, tree_name)
        self.arguments = arguments

    def infer(self):
        values = super().infer()
        if values:
            return values

        return self.get_executed_param_name().infer()

    def get_executed_param_name(self):
        from jedi.inference.param import get_executed_param_names
        params_names = get_executed_param_names(self.function_value, self.arguments)
        return params_names[self._get_param_node().position_index]


class ParamNameWrapper(_ParamMixin):
    def __init__(self, param_name):
        self._wrapped_param_name = param_name

    def __getattr__(self, name):
        return getattr(self._wrapped_param_name, name)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._wrapped_param_name)


class ImportName(AbstractNameDefinition):
    start_pos = (1, 0)
    _level = 0

    def __init__(self, parent_context, string_name):
        self._from_module_context = parent_context
        self.string_name = string_name

    def get_qualified_names(self, include_module_names=False):
        if include_module_names:
            if self._level:
                assert self._level == 1, "Everything else is not supported for now"
                module_names = self._from_module_context.string_names
                if module_names is None:
                    return module_names
                return module_names + (self.string_name,)
            return (self.string_name,)
        return ()

    @property
    def parent_context(self):
        m = self._from_module_context
        import_values = self.infer()
        if not import_values:
            return m
        # It's almost always possible to find the import or to not find it. The
        # importing returns only one value, pretty much always.
        return next(iter(import_values)).as_context()

    @memoize_method
    def infer(self):
        from jedi.inference.imports import Importer
        m = self._from_module_context
        return Importer(m.inference_state, [self.string_name], m, level=self._level).follow()

    def goto(self):
        return [m.name for m in self.infer()]

    @property
    def api_type(self):
        return 'module'

    def py__doc__(self):
        return _merge_name_docs(self.goto())


class SubModuleName(ImportName):
    _level = 1


class NameWrapper:
    def __init__(self, wrapped_name):
        self._wrapped_name = wrapped_name

    def __getattr__(self, name):
        return getattr(self._wrapped_name, name)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._wrapped_name)


class StubNameMixin:
    def py__doc__(self):
```
