# Chunk: ba1db6be2cd3_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/signature.py`
- lines: 90-153
- chunk: 2/2

```
fix=False)

    @memoize_method
    def get_param_names(self, resolve_stars=False):
        params = self._function_value.get_param_names()
        if resolve_stars:
            from jedi.inference.star_args import process_params
            params = process_params(params)
        if self.is_bound:
            return params[1:]
        return params

    def matches_signature(self, arguments):
        from jedi.inference.param import get_executed_param_names_and_issues
        executed_param_names, issues = \
            get_executed_param_names_and_issues(self._function_value, arguments)
        if issues:
            return False

        matches = all(executed_param_name.matches_signature()
                      for executed_param_name in executed_param_names)
        if debug.enable_notice:
            tree_node = self._function_value.tree_node
            signature = parser_utils.get_signature(tree_node)
            if matches:
                debug.dbg("Overloading match: %s@%s (%s)",
                          signature, tree_node.start_pos[0], arguments, color='BLUE')
            else:
                debug.dbg("Overloading no match: %s@%s (%s)",
                          signature, tree_node.start_pos[0], arguments, color='BLUE')
        return matches


class BuiltinSignature(AbstractSignature):
    def __init__(self, value, return_string, function_value=None, is_bound=False):
        super().__init__(value, is_bound)
        self._return_string = return_string
        self.__function_value = function_value

    @property
    def annotation_string(self):
        return self._return_string

    @property
    def _function_value(self):
        if self.__function_value is None:
            return self.value
        return self.__function_value

    def bind(self, value):
        return BuiltinSignature(
            value, self._return_string,
            function_value=self.value,
            is_bound=True
        )


class SignatureWrapper(_SignatureMixin):
    def __init__(self, wrapped_signature):
        self._wrapped_signature = wrapped_signature

    def __getattr__(self, name):
        return getattr(self._wrapped_signature, name)
```
