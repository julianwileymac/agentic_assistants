# Chunk: f0bcaff45f4a_0

- source: `.venv-lab/Lib/site-packages/jedi/api/refactoring/__init__.py`
- lines: 1-88
- chunk: 1/4

```
import difflib
from pathlib import Path
from typing import Dict, Iterable, Tuple

from parso import split_lines

from jedi.api.exceptions import RefactoringError
from jedi.inference.value.namespace import ImplicitNSName

EXPRESSION_PARTS = (
    'or_test and_test not_test comparison '
    'expr xor_expr and_expr shift_expr arith_expr term factor power atom_expr'
).split()


class ChangedFile:
    def __init__(self, inference_state, from_path, to_path,
                 module_node, node_to_str_map):
        self._inference_state = inference_state
        self._from_path = from_path
        self._to_path = to_path
        self._module_node = module_node
        self._node_to_str_map = node_to_str_map

    def get_diff(self):
        old_lines = split_lines(self._module_node.get_code(), keepends=True)
        new_lines = split_lines(self.get_new_code(), keepends=True)

        # Add a newline at the end if it's missing. Otherwise the diff will be
        # very weird. A `diff -u file1 file2` would show the string:
        #
        #     \ No newline at end of file
        #
        # This is not necessary IMO, because Jedi does not really play with
        # newlines and the ending newline does not really matter in Python
        # files. ~dave
        if old_lines[-1] != '':
            old_lines[-1] += '\n'
        if new_lines[-1] != '':
            new_lines[-1] += '\n'

        project_path = self._inference_state.project.path
        if self._from_path is None:
            from_p = ''
        else:
            try:
                from_p = self._from_path.relative_to(project_path)
            except ValueError:  # Happens it the path is not on th project_path
                from_p = self._from_path
        if self._to_path is None:
            to_p = ''
        else:
            try:
                to_p = self._to_path.relative_to(project_path)
            except ValueError:
                to_p = self._to_path
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=str(from_p),
            tofile=str(to_p),
        )
        # Apparently there's a space at the end of the diff - for whatever
        # reason.
        return ''.join(diff).rstrip(' ')

    def get_new_code(self):
        return self._inference_state.grammar.refactor(self._module_node, self._node_to_str_map)

    def apply(self):
        if self._from_path is None:
            raise RefactoringError(
                'Cannot apply a refactoring on a Script with path=None'
            )

        with open(self._from_path, 'w', newline='') as f:
            f.write(self.get_new_code())

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._from_path)


class Refactoring:
    def __init__(self, inference_state, file_to_node_changes, renames=()):
        self._inference_state = inference_state
        self._renames = renames
        self._file_to_node_changes = file_to_node_changes
```
