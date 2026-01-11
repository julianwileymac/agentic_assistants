# Chunk: f6cd2cb7ea21_0

- source: `.venv-lab/Lib/site-packages/jedi/api/project.py`
- lines: 1-85
- chunk: 1/7

```
"""
Projects are a way to handle Python projects within Jedi. For simpler plugins
you might not want to deal with projects, but if you want to give the user more
flexibility to define sys paths and Python interpreters for a project,
:class:`.Project` is the perfect way to allow for that.

Projects can be saved to disk and loaded again, to allow project definitions to
be used across repositories.
"""
import json
from pathlib import Path
from itertools import chain

from jedi import debug
from jedi.api.environment import get_cached_default_environment, create_environment
from jedi.api.exceptions import WrongVersion
from jedi.api.completion import search_in_module
from jedi.api.helpers import split_search_string, get_module_names
from jedi.inference.imports import load_module_from_path, \
    load_namespace_from_path, iter_module_names
from jedi.inference.sys_path import discover_buildout_paths
from jedi.inference.cache import inference_state_as_method_param_cache
from jedi.inference.references import recurse_find_python_folders_and_files, search_in_file_ios
from jedi.file_io import FolderIO

_CONFIG_FOLDER = '.jedi'
_CONTAINS_POTENTIAL_PROJECT = \
    'setup.py', '.git', '.hg', 'requirements.txt', 'MANIFEST.in', 'pyproject.toml'

_SERIALIZER_VERSION = 1


def _try_to_skip_duplicates(func):
    def wrapper(*args, **kwargs):
        found_tree_nodes = []
        found_modules = []
        for definition in func(*args, **kwargs):
            tree_node = definition._name.tree_name
            if tree_node is not None and tree_node in found_tree_nodes:
                continue
            if definition.type == 'module' and definition.module_path is not None:
                if definition.module_path in found_modules:
                    continue
                found_modules.append(definition.module_path)
            yield definition
            found_tree_nodes.append(tree_node)
    return wrapper


def _remove_duplicates_from_path(path):
    used = set()
    for p in path:
        if p in used:
            continue
        used.add(p)
        yield p


class Project:
    """
    Projects are a simple way to manage Python folders and define how Jedi does
    import resolution. It is mostly used as a parameter to :class:`.Script`.
    Additionally there are functions to search a whole project.
    """
    _environment = None

    @staticmethod
    def _get_config_folder_path(base_path):
        return base_path.joinpath(_CONFIG_FOLDER)

    @staticmethod
    def _get_json_path(base_path):
        return Project._get_config_folder_path(base_path).joinpath('project.json')

    @classmethod
    def load(cls, path):
        """
        Loads a project from a specific path. You should not provide the path
        to ``.jedi/project.json``, but rather the path to the project folder.

        :param path: The path of the directory you want to use as a project.
        """
        if isinstance(path, str):
            path = Path(path)
```
