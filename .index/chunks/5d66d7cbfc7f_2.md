# Chunk: 5d66d7cbfc7f_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/__init__.py`
- lines: 128-196
- chunk: 3/4

```
        module_name = 'builtins'
        builtins_module, = self.import_module((module_name,), sys_path=[])
        return builtins_module

    @property  # type: ignore[misc]
    @inference_state_function_cache()
    def typing_module(self):
        typing_module, = self.import_module(('typing',))
        return typing_module

    def reset_recursion_limitations(self):
        self.recursion_detector = recursion.RecursionDetector()
        self.execution_recursion_detector = recursion.ExecutionRecursionDetector(self)

    def get_sys_path(self, **kwargs):
        """Convenience function"""
        return self.project._get_sys_path(self, **kwargs)

    def infer(self, context, name):
        def_ = name.get_definition(import_name_always=True)
        if def_ is not None:
            type_ = def_.type
            is_classdef = type_ == 'classdef'
            if is_classdef or type_ == 'funcdef':
                if is_classdef:
                    c = ClassValue(self, context, name.parent)
                else:
                    c = FunctionValue.from_context(context, name.parent)
                return ValueSet([c])

            if type_ == 'expr_stmt':
                is_simple_name = name.parent.type not in ('power', 'trailer')
                if is_simple_name:
                    return infer_expr_stmt(context, def_, name)
            if type_ == 'for_stmt':
                container_types = context.infer_node(def_.children[3])
                cn = ContextualizedNode(context, def_.children[3])
                for_types = iterate_values(container_types, cn)
                n = TreeNameDefinition(context, name)
                return check_tuple_assignments(n, for_types)
            if type_ in ('import_from', 'import_name'):
                return imports.infer_import(context, name)
            if type_ == 'with_stmt':
                return tree_name_to_values(self, context, name)
            elif type_ == 'param':
                return context.py__getattribute__(name.value, position=name.end_pos)
            elif type_ == 'namedexpr_test':
                return context.infer_node(def_)
        else:
            result = follow_error_node_imports_if_possible(context, name)
            if result is not None:
                return result

        return helpers.infer_call_of_leaf(context, name)

    def parse_and_get_code(self, code=None, path=None,
                           use_latest_grammar=False, file_io=None, **kwargs):
        if code is None:
            if file_io is None:
                file_io = FileIO(path)
            code = file_io.read()
        # We cannot just use parso, because it doesn't use errors='replace'.
        code = parso.python_bytes_to_unicode(code, encoding='utf-8', errors='replace')

        if len(code) > settings._cropped_file_size:
            code = code[:settings._cropped_file_size]

        grammar = self.latest_grammar if use_latest_grammar else self.grammar
```
