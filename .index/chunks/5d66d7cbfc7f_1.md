# Chunk: 5d66d7cbfc7f_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/__init__.py`
- lines: 62-136
- chunk: 2/4

```
statements and modules
that are not used are just being ignored.
"""
import parso
from jedi.file_io import FileIO

from jedi import debug
from jedi import settings
from jedi.inference import imports
from jedi.inference import recursion
from jedi.inference.cache import inference_state_function_cache
from jedi.inference import helpers
from jedi.inference.names import TreeNameDefinition
from jedi.inference.base_value import ContextualizedNode, \
    ValueSet, iterate_values
from jedi.inference.value import ClassValue, FunctionValue
from jedi.inference.syntax_tree import infer_expr_stmt, \
    check_tuple_assignments, tree_name_to_values
from jedi.inference.imports import follow_error_node_imports_if_possible
from jedi.plugins import plugin_manager


class InferenceState:
    def __init__(self, project, environment=None, script_path=None):
        if environment is None:
            environment = project.get_environment()
        self.environment = environment
        self.script_path = script_path
        self.compiled_subprocess = environment.get_inference_state_subprocess(self)
        self.grammar = environment.get_grammar()

        self.latest_grammar = parso.load_grammar(version='3.13')
        self.memoize_cache = {}  # for memoize decorators
        self.module_cache = imports.ModuleCache()  # does the job of `sys.modules`.
        self.stub_module_cache = {}  # Dict[Tuple[str, ...], Optional[ModuleValue]]
        self.compiled_cache = {}  # see `inference.compiled.create()`
        self.inferred_element_counts = {}
        self.mixed_cache = {}  # see `inference.compiled.mixed._create()`
        self.analysis = []
        self.dynamic_params_depth = 0
        self.do_dynamic_params_search = settings.dynamic_params
        self.is_analysis = False
        self.project = project
        self.access_cache = {}
        self.allow_unsafe_executions = False
        self.flow_analysis_enabled = True

        self.reset_recursion_limitations()

    def import_module(self, import_names, sys_path=None, prefer_stubs=True):
        return imports.import_module_by_names(
            self, import_names, sys_path, prefer_stubs=prefer_stubs)

    @staticmethod
    @plugin_manager.decorate()
    def execute(value, arguments):
        debug.dbg('execute: %s %s', value, arguments)
        with debug.increase_indent_cm():
            value_set = value.py__call__(arguments=arguments)
        debug.dbg('execute result: %s in %s', value_set, value)
        return value_set

    # mypy doesn't suppport decorated propeties (https://github.com/python/mypy/issues/1362)
    @property  # type: ignore[misc]
    @inference_state_function_cache()
    def builtins_module(self):
        module_name = 'builtins'
        builtins_module, = self.import_module((module_name,), sys_path=[])
        return builtins_module

    @property  # type: ignore[misc]
    @inference_state_function_cache()
    def typing_module(self):
        typing_module, = self.import_module(('typing',))
```
