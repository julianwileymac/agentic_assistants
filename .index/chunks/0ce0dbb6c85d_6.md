# Chunk: 0ce0dbb6c85d_6

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 461-548
- chunk: 7/9

```
er_param
        values = infer_param(
            self.function_value, self._get_param_node(),
            ignore_stars=ignore_stars)
        if execute_annotation:
            values = values.execute_annotation()
        return values

    def infer_default(self):
        node = self.default_node
        if node is None:
            return NO_VALUES
        return self.parent_context.infer_node(node)

    @property
    def default_node(self):
        return self._get_param_node().default

    def get_kind(self):
        tree_param = self._get_param_node()
        if tree_param.star_count == 1:  # *args
            return Parameter.VAR_POSITIONAL
        if tree_param.star_count == 2:  # **kwargs
            return Parameter.VAR_KEYWORD

        # Params starting with __ are an equivalent to positional only
        # variables in typeshed.
        if tree_param.name.value.startswith('__'):
            return Parameter.POSITIONAL_ONLY

        parent = tree_param.parent
        param_appeared = False
        for p in parent.children:
            if param_appeared:
                if p == '/':
                    return Parameter.POSITIONAL_ONLY
            else:
                if p == '*':
                    return Parameter.KEYWORD_ONLY
                if p.type == 'param':
                    if p.star_count:
                        return Parameter.KEYWORD_ONLY
                    if p == tree_param:
                        param_appeared = True
        return Parameter.POSITIONAL_OR_KEYWORD

    def infer(self):
        values = self.infer_annotation()
        if values:
            return values

        doc_params = docstrings.infer_param(self.function_value, self._get_param_node())
        return doc_params


class AnonymousParamName(_ActualTreeParamName):
    @plugin_manager.decorate(name='goto_anonymous_param')
    def goto(self):
        return super().goto()

    @plugin_manager.decorate(name='infer_anonymous_param')
    def infer(self):
        values = super().infer()
        if values:
            return values
        from jedi.inference.dynamic_params import dynamic_param_lookup
        param = self._get_param_node()
        values = dynamic_param_lookup(self.function_value, param.position_index)
        if values:
            return values

        if param.star_count == 1:
            from jedi.inference.value.iterable import FakeTuple
            value = FakeTuple(self.function_value.inference_state, [])
        elif param.star_count == 2:
            from jedi.inference.value.iterable import FakeDict
            value = FakeDict(self.function_value.inference_state, {})
        elif param.default is None:
            return NO_VALUES
        else:
            return self.function_value.parent_context.infer_node(param.default)
        return ValueSet({value})


class ParamName(_ActualTreeParamName):
    def __init__(self, function_value, tree_name, arguments):
        super().__init__(function_value, tree_name)
```
