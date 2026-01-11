# Chunk: e370edcf8fd5_0

- source: `.venv-lab/Lib/site-packages/jedi/inference/filters.py`
- lines: 1-91
- chunk: 1/5

```
"""
Filters are objects that you can use to filter names in different scopes. They
are needed for name resolution.
"""
from abc import abstractmethod
from typing import List, MutableMapping, Type
import weakref

from parso.tree import search_ancestor
from parso.python.tree import Name, UsedNamesMapping

from jedi.inference import flow_analysis
from jedi.inference.base_value import ValueSet, ValueWrapper, \
    LazyValueWrapper
from jedi.parser_utils import get_cached_parent_scope, get_parso_cache_node
from jedi.inference.utils import to_list
from jedi.inference.names import TreeNameDefinition, ParamName, \
    AnonymousParamName, AbstractNameDefinition, NameWrapper

_definition_name_cache: MutableMapping[UsedNamesMapping, List[Name]]
_definition_name_cache = weakref.WeakKeyDictionary()


class AbstractFilter:
    _until_position = None

    def _filter(self, names):
        if self._until_position is not None:
            return [n for n in names if n.start_pos < self._until_position]
        return names

    @abstractmethod
    def get(self, name):
        raise NotImplementedError

    @abstractmethod
    def values(self):
        raise NotImplementedError


class FilterWrapper:
    name_wrapper_class: Type[NameWrapper]

    def __init__(self, wrapped_filter):
        self._wrapped_filter = wrapped_filter

    def wrap_names(self, names):
        return [self.name_wrapper_class(name) for name in names]

    def get(self, name):
        return self.wrap_names(self._wrapped_filter.get(name))

    def values(self):
        return self.wrap_names(self._wrapped_filter.values())


def _get_definition_names(parso_cache_node, used_names, name_key):
    if parso_cache_node is None:
        names = used_names.get(name_key, ())
        return tuple(name for name in names if name.is_definition(include_setitem=True))

    try:
        for_module = _definition_name_cache[parso_cache_node]
    except KeyError:
        for_module = _definition_name_cache[parso_cache_node] = {}

    try:
        return for_module[name_key]
    except KeyError:
        names = used_names.get(name_key, ())
        result = for_module[name_key] = tuple(
            name for name in names if name.is_definition(include_setitem=True)
        )
        return result


class _AbstractUsedNamesFilter(AbstractFilter):
    name_class = TreeNameDefinition

    def __init__(self, parent_context, node_context=None):
        if node_context is None:
            node_context = parent_context
        self._node_context = node_context
        self._parser_scope = node_context.tree_node
        module_context = node_context.get_root_context()
        # It is quite hacky that we have to use that. This is for caching
        # certain things with a WeakKeyDictionary. However, parso intentionally
        # uses slots (to save memory) and therefore we end up with having to
        # have a weak reference to the object that caches the tree.
        #
```
