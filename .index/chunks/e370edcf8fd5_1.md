# Chunk: e370edcf8fd5_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/filters.py`
- lines: 86-156
- chunk: 2/5

```
 It is quite hacky that we have to use that. This is for caching
        # certain things with a WeakKeyDictionary. However, parso intentionally
        # uses slots (to save memory) and therefore we end up with having to
        # have a weak reference to the object that caches the tree.
        #
        # Previously we have tried to solve this by using a weak reference onto
        # used_names. However that also does not work, because it has a
        # reference from the module, which itself is referenced by any node
        # through parents.
        path = module_context.py__file__()
        if path is None:
            # If the path is None, there is no guarantee that parso caches it.
            self._parso_cache_node = None
        else:
            self._parso_cache_node = get_parso_cache_node(
                module_context.inference_state.latest_grammar
                if module_context.is_stub() else module_context.inference_state.grammar,
                path
            )
        self._used_names = module_context.tree_node.get_used_names()
        self.parent_context = parent_context

    def get(self, name):
        return self._convert_names(self._filter(
            _get_definition_names(self._parso_cache_node, self._used_names, name),
        ))

    def _convert_names(self, names):
        return [self.name_class(self.parent_context, name) for name in names]

    def values(self):
        return self._convert_names(
            name
            for name_key in self._used_names
            for name in self._filter(
                _get_definition_names(self._parso_cache_node, self._used_names, name_key),
            )
        )

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.parent_context)


class ParserTreeFilter(_AbstractUsedNamesFilter):
    def __init__(self, parent_context, node_context=None, until_position=None,
                 origin_scope=None):
        """
        node_context is an option to specify a second value for use cases
        like the class mro where the parent class of a new name would be the
        value, but for some type inference it's important to have a local
        value of the other classes.
        """
        super().__init__(parent_context, node_context)
        self._origin_scope = origin_scope
        self._until_position = until_position

    def _filter(self, names):
        names = super()._filter(names)
        names = [n for n in names if self._is_name_reachable(n)]
        return list(self._check_flows(names))

    def _is_name_reachable(self, name):
        parent = name.parent
        if parent.type == 'trailer':
            return False
        base_node = parent if parent.type in ('classdef', 'funcdef') else name
        return get_cached_parent_scope(self._parso_cache_node, base_node) == self._parser_scope

    def _check_flows(self, names):
        for name in sorted(names, key=lambda name: name.start_pos, reverse=True):
```
